"""Tests admin_interface/db.py (accès qualité des données pour l'interface admin).

Nécessite un PostgreSQL accessible via DATABASE_URL (une instance jetable,
jamais une base contenant de vraies données : la suite DROP puis recrée
les tables du schéma à chaque exécution, même pattern que
tests/data_quality/test_schema.py).

Usage :
    DATABASE_URL=postgresql://user:pass@host:5432/db pytest tests/admin_interface/test_db.py
"""
import os
from pathlib import Path

import psycopg2
import psycopg2.extras
import pytest

DDL_PATH = Path(__file__).resolve().parents[2] / "database" / "schema" / "ddl_postgres.sql"
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://healthai:changeme@localhost:5432/healthai_coach"
)
# admin_interface.db lit DATABASE_URL au moment de l'import (constante de
# module) : on s'assure qu'elle est fixée avant l'import pour que ses
# fonctions ouvrent leurs connexions vers la même base que cette suite.
os.environ.setdefault("DATABASE_URL", DATABASE_URL)

from admin_interface import db as admin_db  # noqa: E402

EXPECTED_TABLES = {
    "users", "food_items", "nutrition_logs", "exercises", "workout_sessions",
    "workout_sets", "biometric_measurements", "medical_profiles",
    "dietary_preferences", "fitness_profiles", "diet_recommendations",
    "data_quality_log", "organizations", "subscriptions",
    "workout_plans", "nutrition_plans",
}


@pytest.fixture(scope="module")
def db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cur:
        cur.execute(f"DROP TABLE IF EXISTS {', '.join(EXPECTED_TABLES)} CASCADE")
        cur.execute(DDL_PATH.read_text())
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def seeded(db_connection):
    """1 admin, 1 utilisateur normal, 3 anomalies à detected_at distincts
    (dont 1 déjà résolue) — pour tester filtres et tri sans ambiguïté."""
    with db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            "INSERT INTO users (email, hashed_password, first_name, last_name, is_admin) "
            "VALUES ('admin@test.local', 'x', 'Admin', 'Test', TRUE) RETURNING user_id"
        )
        admin_id = cur.fetchone()["user_id"]
        cur.execute(
            "INSERT INTO users (email, hashed_password, first_name, last_name) "
            "VALUES ('user@test.local', 'x', 'Regular', 'User')"
        )

        cur.execute(
            "INSERT INTO data_quality_log (source_table, rule_name, severity, message, detected_at) "
            "VALUES ('food_items', 'check_range', 'warning', 'anomalie 1', now() - interval '2 hours') "
            "RETURNING dq_log_id"
        )
        log_1 = cur.fetchone()["dq_log_id"]
        cur.execute(
            "INSERT INTO data_quality_log (source_table, rule_name, severity, message, detected_at) "
            "VALUES ('nutrition_logs', 'check_fk', 'error', 'anomalie 2', now() - interval '1 hour') "
            "RETURNING dq_log_id"
        )
        log_2 = cur.fetchone()["dq_log_id"]
        cur.execute(
            "INSERT INTO data_quality_log "
            "(source_table, rule_name, severity, message, detected_at, resolved, resolved_at, resolved_by) "
            "VALUES ('exercises', 'check_range', 'info', 'anomalie 3', now(), TRUE, now(), %s) "
            "RETURNING dq_log_id",
            (admin_id,),
        )
        log_3 = cur.fetchone()["dq_log_id"]
    db_connection.commit()
    yield {"admin_id": admin_id, "log_1": log_1, "log_2": log_2, "log_3": log_3}
    with db_connection.cursor() as cur:
        cur.execute("TRUNCATE TABLE data_quality_log, users RESTART IDENTITY CASCADE")
    db_connection.commit()


def test_list_admin_users_returns_only_admins(seeded):
    admins = admin_db.list_admin_users()
    assert len(admins) == 1
    assert admins[0]["email"] == "admin@test.local"
    assert admins[0]["user_id"] == seeded["admin_id"]


def test_list_data_quality_log_returns_all_by_default(seeded):
    rows = admin_db.list_data_quality_log()
    assert len(rows) == 3


def test_list_data_quality_log_filters_by_severity(seeded):
    rows = admin_db.list_data_quality_log(severity="error")
    assert len(rows) == 1
    assert rows[0]["dq_log_id"] == seeded["log_2"]


def test_list_data_quality_log_filters_by_resolved(seeded):
    resolved = admin_db.list_data_quality_log(resolved=True)
    assert [r["dq_log_id"] for r in resolved] == [seeded["log_3"]]

    unresolved = admin_db.list_data_quality_log(resolved=False)
    assert {r["dq_log_id"] for r in unresolved} == {seeded["log_1"], seeded["log_2"]}


def test_list_data_quality_log_filters_by_source_table_partial_match(seeded):
    rows = admin_db.list_data_quality_log(source_table="food")
    assert len(rows) == 1
    assert rows[0]["dq_log_id"] == seeded["log_1"]


def test_list_data_quality_log_orders_by_detected_at_desc(seeded):
    rows = admin_db.list_data_quality_log()
    assert [r["dq_log_id"] for r in rows] == [seeded["log_3"], seeded["log_2"], seeded["log_1"]]


def test_list_data_quality_log_respects_limit(seeded):
    rows = admin_db.list_data_quality_log(limit=1)
    assert len(rows) == 1
    assert rows[0]["dq_log_id"] == seeded["log_3"]


def test_resolve_entry_marks_resolved_and_sets_resolved_by(seeded):
    ok = admin_db.resolve_entry(seeded["log_1"], resolved_by=seeded["admin_id"])
    assert ok is True

    rows = admin_db.list_data_quality_log(resolved=True)
    resolved_row = next(r for r in rows if r["dq_log_id"] == seeded["log_1"])
    assert resolved_row["resolved_by"] == seeded["admin_id"]
    assert resolved_row["resolved_at"] is not None


def test_resolve_entry_returns_false_for_unknown_id(seeded):
    ok = admin_db.resolve_entry(999999)
    assert ok is False


def test_resolve_entry_without_resolved_by_is_allowed(seeded):
    ok = admin_db.resolve_entry(seeded["log_2"], resolved_by=None)
    assert ok is True
    rows = admin_db.list_data_quality_log(resolved=True)
    row = next(r for r in rows if r["dq_log_id"] == seeded["log_2"])
    assert row["resolved_by"] is None
    assert row["resolved_at"] is not None

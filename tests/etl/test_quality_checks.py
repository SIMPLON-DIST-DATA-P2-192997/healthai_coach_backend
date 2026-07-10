"""Tests etl/quality/checks.py contre un vrai PostgreSQL.

Nécessite un PostgreSQL accessible via DATABASE_URL (une instance jetable,
jamais une base contenant de vraies données : la suite DROP puis recrée
les tables du schéma à chaque exécution, même pattern que
tests/data_quality/test_schema.py et tests/admin_interface/test_db.py).
Les règles portent sur des seuils métier (calories > 2000, body_fat_pct
> 60) : seule une vraie base garantit que les lignes correspondantes
existent effectivement.
"""
import os
from pathlib import Path

import psycopg2
import psycopg2.extras
import pytest

DDL_PATH = Path(__file__).resolve().parents[2] / "database" / "schema" / "ddl_postgres.sql"
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL doit être défini explicitement (instance Postgres jetable) — "
        "cette suite fait DROP TABLE ... CASCADE à chaque exécution (cf. docstring "
        "du module), pas de valeur par défaut pointant vers une base pouvant "
        "contenir de vraies données."
    )
os.environ.setdefault("DATABASE_URL", DATABASE_URL)

from etl.quality.checks import run_quality_checks  # noqa: E402

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


def _log_rows(db_connection, rule_name):
    with db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            "SELECT * FROM data_quality_log WHERE rule_name = %s ORDER BY dq_log_id", (rule_name,)
        )
        return cur.fetchall()


def test_check_tables_not_empty_flags_empty_tables(db_connection):
    """Tables fraîchement créées, aucune donnée chargée : les 3 tables
    surveillées doivent être signalées en erreur."""
    run_quality_checks(dag_id="test_dag")
    db_connection.commit()

    rows = _log_rows(db_connection, "check_table_not_empty")
    flagged_tables = {row["source_table"] for row in rows}
    assert flagged_tables == {"users", "food_items", "exercises"}
    assert all(row["severity"] == "error" for row in rows)
    assert all(row["dag_id"] == "test_dag" for row in rows)

    with db_connection.cursor() as cur:
        cur.execute("TRUNCATE TABLE data_quality_log RESTART IDENTITY CASCADE")
    db_connection.commit()


@pytest.fixture
def seeded(db_connection):
    with db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            "INSERT INTO users (email, hashed_password, first_name, last_name) "
            "VALUES ('u1@test.local', 'x', 'A', 'B') RETURNING user_id"
        )
        user_id = cur.fetchone()["user_id"]

        cur.execute(
            "INSERT INTO food_items (source, name, category, calories_kcal) "
            "VALUES ('test', 'Normal Food', 'Fruit', 500)"
        )
        cur.execute(
            "INSERT INTO food_items (source, name, category, calories_kcal) "
            "VALUES ('test', 'Outlier Food', NULL, 2500) RETURNING food_item_id"
        )
        outlier_food_id = cur.fetchone()["food_item_id"]

        cur.execute("INSERT INTO exercises (source, name) VALUES ('test', 'Push-up')")

        cur.execute(
            "INSERT INTO biometric_measurements (user_id, measured_at, body_fat_pct) "
            "VALUES (%s, now() - interval '1 hour', 20)", (user_id,),
        )
        cur.execute(
            "INSERT INTO biometric_measurements (user_id, measured_at, body_fat_pct) "
            "VALUES (%s, now(), 75) RETURNING measurement_id", (user_id,),
        )
        outlier_measurement_id = cur.fetchone()["measurement_id"]
    db_connection.commit()

    yield {"outlier_food_id": outlier_food_id, "outlier_measurement_id": outlier_measurement_id}

    with db_connection.cursor() as cur:
        cur.execute(
            "TRUNCATE TABLE data_quality_log, biometric_measurements, food_items, "
            "exercises, users RESTART IDENTITY CASCADE"
        )
    db_connection.commit()


def test_check_outlier_calories_flags_only_the_outlier(db_connection, seeded):
    run_quality_checks(dag_id="test_dag")
    db_connection.commit()

    rows = _log_rows(db_connection, "check_outlier_calories")
    assert len(rows) == 1
    assert rows[0]["source_record_id"] == str(seeded["outlier_food_id"])
    assert rows[0]["severity"] == "warning"


def test_check_outlier_body_fat_flags_only_the_outlier(db_connection, seeded):
    run_quality_checks(dag_id="test_dag")
    db_connection.commit()

    rows = _log_rows(db_connection, "check_outlier_body_fat")
    assert len(rows) == 1
    assert rows[0]["source_record_id"] == str(seeded["outlier_measurement_id"])
    assert rows[0]["severity"] == "warning"


def test_check_missing_category_counts_null_rows(db_connection, seeded):
    run_quality_checks(dag_id="test_dag")
    db_connection.commit()

    rows = _log_rows(db_connection, "check_missing_category")
    assert len(rows) == 1
    assert "1 food_items" in rows[0]["message"]
    assert rows[0]["severity"] == "info"


def test_check_tables_not_empty_silent_once_seeded(db_connection, seeded):
    run_quality_checks(dag_id="test_dag")
    db_connection.commit()

    assert _log_rows(db_connection, "check_table_not_empty") == []

"""Tests Sprint 1 : création des tables + contraintes FK/CHECK.

Nécessite un PostgreSQL accessible via DATABASE_URL (une instance jetable,
jamais une base contenant de vraies données : la suite DROP puis recrée
les tables du schéma à chaque exécution).

Usage :
    DATABASE_URL=postgresql://user:pass@host:5432/db pytest tests/data_quality/test_schema.py
"""

import os
from pathlib import Path

import psycopg2
import pytest

DDL_PATH = Path(__file__).resolve().parents[2] / "database" / "schema" / "ddl_postgres.sql"
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://healthai:changeme@localhost:5432/healthai_coach"
)

EXPECTED_TABLES = {
    "users",
    "food_items",
    "nutrition_logs",
    "exercises",
    "workout_sessions",
    "workout_sets",
    "biometric_measurements",
    "medical_profiles",
    "dietary_preferences",
    "fitness_profiles",
    "diet_recommendations",
    "data_quality_log",
    "organizations",
    "subscriptions",
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
def cursor(db_connection):
    """Curseur par test, avec rollback systématique pour isoler les tests entre eux."""
    with db_connection.cursor() as cur:
        yield cur
    db_connection.rollback()


def test_all_tables_created(db_connection):
    with db_connection.cursor() as cur:
        cur.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """
        )
        tables = {row[0] for row in cur.fetchall()}
    missing = EXPECTED_TABLES - tables
    assert not missing, f"Tables manquantes après application du DDL : {missing}"


def test_nutrition_logs_rejects_invalid_foreign_keys(cursor):
    with pytest.raises(psycopg2.errors.ForeignKeyViolation):
        cursor.execute(
            """
            INSERT INTO nutrition_logs (user_id, food_item_id, portion_number, meal_type, logged_at)
            VALUES (999999, 999999, 1.5, 'lunch', now())
            """
        )


def test_biometric_measurements_rejects_invalid_user_fk(cursor):
    with pytest.raises(psycopg2.errors.ForeignKeyViolation):
        cursor.execute(
            """
            INSERT INTO biometric_measurements (user_id, measured_at, weight_kg)
            VALUES (999999, now(), 70)
            """
        )


def test_deleting_user_cascades_to_nutrition_logs(db_connection):
    with db_connection.cursor() as cur:
        cur.execute(
            "INSERT INTO users (email, hashed_password, first_name, last_name) "
            "VALUES ('cascade-test@example.com', 'x', 'A', 'B') RETURNING user_id"
        )
        user_id = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO food_items (source, name, calories_kcal) VALUES ('test', 'Test Food', 100) "
            "RETURNING food_item_id"
        )
        food_item_id = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO nutrition_logs (user_id, food_item_id, portion_number, meal_type, logged_at) "
            "VALUES (%s, %s, 1.5, 'lunch', now())",
            (user_id, food_item_id),
        )
        cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        cur.execute("SELECT COUNT(*) FROM nutrition_logs WHERE user_id = %s", (user_id,))
        assert cur.fetchone()[0] == 0, "ON DELETE CASCADE n'a pas supprimé les nutrition_logs du user"
    db_connection.rollback()


def test_data_quality_log_resolution_consistency_check(cursor):
    with pytest.raises(psycopg2.errors.CheckViolation):
        cursor.execute(
            """
            INSERT INTO data_quality_log (source_table, rule_name, severity, message, resolved, resolved_at)
            VALUES ('food_items', 'check_range', 'info', 'incohérent', FALSE, now())
            """
        )


def test_data_quality_log_accepts_consistent_rows(cursor):
    cursor.execute(
        """
        INSERT INTO data_quality_log (source_table, rule_name, severity, message)
        VALUES ('food_items', 'check_range', 'info', 'non résolu, valide')
        """
    )
    cursor.execute(
        """
        INSERT INTO data_quality_log (source_table, rule_name, severity, message, resolved, resolved_at)
        VALUES ('food_items', 'check_range', 'info', 'résolu, valide', TRUE, now())
        """
    )

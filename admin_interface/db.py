"""Accès base de données pour l'interface admin (consultation qualité).

Usage attendu : DATABASE_URL pointant vers le PostgreSQL du projet (déjà
peuplé via database/seed/ ou l'ETL réel).
"""

import os

import psycopg2
import psycopg2.extras

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://healthai:changeme@localhost:5432/healthai_coach"
)

SEVERITIES = ["info", "warning", "error", "critical"]


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def list_data_quality_log(severity=None, resolved=None, source_table=None, limit=200):
    """Retourne les entrées de data_quality_log filtrées, triées par date de
    détection décroissante."""
    query = """
        SELECT dq_log_id, source_table, source_record_id, dag_id, rule_name,
               severity, message, detected_at, resolved, resolved_at, resolved_by
        FROM data_quality_log
        WHERE (%(severity)s IS NULL OR severity = %(severity)s)
          AND (%(resolved)s IS NULL OR resolved = %(resolved)s)
          AND (%(source_table)s IS NULL OR source_table ILIKE %(source_table)s)
        ORDER BY detected_at DESC
        LIMIT %(limit)s
    """
    params = {
        "severity": severity or None,
        "resolved": resolved,
        "source_table": f"%{source_table}%" if source_table else None,
        "limit": limit,
    }
    with get_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]


def list_admin_users():
    """Retourne les utilisateurs admin (pour renseigner resolved_by)."""
    with get_connection() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT user_id, email FROM users WHERE is_admin = TRUE ORDER BY email")
        return [dict(row) for row in cur.fetchall()]


def resolve_entry(dq_log_id, resolved_by=None):
    """Marque une anomalie comme résolue.

    Respecte chk_data_quality_log_resolution_consistency : resolved passe à
    TRUE en même temps que resolved_at/resolved_by sont renseignés, jamais
    l'un sans l'autre.
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            UPDATE data_quality_log
            SET resolved = TRUE, resolved_at = now(), resolved_by = %s
            WHERE dq_log_id = %s
            """,
            (resolved_by, dq_log_id),
        )
        conn.commit()
        return cur.rowcount > 0

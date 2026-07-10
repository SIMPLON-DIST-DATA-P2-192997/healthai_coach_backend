"""Contrôle qualité post-chargement.

Quelques règles simples qui journalisent leurs résultats dans
data_quality_log plutôt que de bloquer le pipeline — cohérent avec le
rôle de cette table (consultation/résolution via l'interface admin,
Sprint 5), pas une porte de blocage du DAG.

Les contraintes CHECK du schéma (cf. database/schema/ddl_postgres.sql)
empêchent déjà l'insertion de valeurs manifestement invalides (négatives,
hors plage) : une règle "valeur négative" post-chargement ne trouverait
donc jamais rien, ces lignes n'auraient jamais pu être insérées. Les
règles ci-dessous portent sur des valeurs plausibles mais suspectes, ou
sur des indicateurs de complétude — pas sur ce que CHECK couvre déjà.
"""
import os

import psycopg2

# Tables alimentées par etl/load/postgres_loader.py : une table vide après
# un chargement qui prétend avoir réussi est en soi une anomalie.
NON_EMPTY_TABLES = ["users", "food_items", "exercises"]


def _log(cur, source_table, rule_name, severity, message, source_record_id=None, dag_id=None):
    cur.execute(
        """
        INSERT INTO data_quality_log
            (source_table, source_record_id, dag_id, rule_name, severity, message)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (source_table, source_record_id, dag_id, rule_name, severity, message),
    )


def check_tables_not_empty(cur, dag_id=None):
    for table in NON_EMPTY_TABLES:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        if count == 0:
            _log(
                cur, table, "check_table_not_empty", "error",
                f"Table '{table}' vide après chargement.", dag_id=dag_id,
            )


def check_outlier_calories(cur, dag_id=None):
    """Valeur plausible au sens de CHECK (>= 0) mais suspecte pour une
    portion de référence unique."""
    cur.execute("SELECT food_item_id, calories_kcal FROM food_items WHERE calories_kcal > 2000")
    for food_item_id, calories in cur.fetchall():
        _log(
            cur, "food_items", "check_outlier_calories", "warning",
            f"calories_kcal={calories} très élevé pour une portion (food_item_id={food_item_id}).",
            source_record_id=str(food_item_id), dag_id=dag_id,
        )


def check_outlier_body_fat(cur, dag_id=None):
    """body_fat_pct est contraint à [0, 100] par CHECK, mais au-delà de ~60
    la valeur est médicalement implausible sans être hors plage."""
    cur.execute(
        "SELECT measurement_id, body_fat_pct FROM biometric_measurements WHERE body_fat_pct > 60"
    )
    for measurement_id, pct in cur.fetchall():
        _log(
            cur, "biometric_measurements", "check_outlier_body_fat", "warning",
            f"body_fat_pct={pct} médicalement implausible (measurement_id={measurement_id}).",
            source_record_id=str(measurement_id), dag_id=dag_id,
        )


def check_missing_category(cur, dag_id=None):
    """category est nullable en base : une absence n'est pas une erreur de
    chargement, mais une lacune de complétude à signaler (info)."""
    cur.execute("SELECT COUNT(*) FROM food_items WHERE category IS NULL")
    count = cur.fetchone()[0]
    if count > 0:
        _log(
            cur, "food_items", "check_missing_category", "info",
            f"{count} food_items sans category renseignée.", dag_id=dag_id,
        )


def run_quality_checks(dag_id=None):
    """Point d'entrée : exécute toutes les règles et committe les anomalies
    trouvées dans data_quality_log. Ne lève jamais d'exception pour un
    résultat de check (une anomalie détectée n'est pas un échec de
    pipeline) — seule une erreur de connexion/SQL fait échouer la tâche."""
    database_url = os.environ.get(
        "DATABASE_URL", "postgresql://healthai:changeme@localhost:5432/healthai_coach"
    )
    conn = psycopg2.connect(database_url)
    try:
        with conn:
            with conn.cursor() as cur:
                check_tables_not_empty(cur, dag_id=dag_id)
                check_outlier_calories(cur, dag_id=dag_id)
                check_outlier_body_fat(cur, dag_id=dag_id)
                check_missing_category(cur, dag_id=dag_id)
        print("✅ Contrôle qualité terminé.")
    finally:
        conn.close()


if __name__ == "__main__":
    run_quality_checks()

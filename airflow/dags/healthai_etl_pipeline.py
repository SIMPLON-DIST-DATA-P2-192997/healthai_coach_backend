"""DAG unique : extraction -> transformation+chargement -> contrôle qualité.

Un seul DAG plutôt qu'un DAG par source (choix documenté dans le rapport,
section Pipeline ETL) : le volume de données et le nombre de sources ne
justifient pas la complexité d'une orchestration par source pour ce
projet. Les trois étapes s'enchaînent en séquence ; chacune fait échouer
le DAG entier en cas d'erreur (code de sortie non nul du process lancé
par BashOperator).

transform et load sont une seule tâche ("transform_and_load") plutôt que
deux : etl/load/postgres_loader.py transforme puis charge dans le même
processus, sans écrire d'artefact intermédiaire sur disque entre les deux
— les séparer forcerait à faire transiter des DataFrames pandas par XCom,
déconseillé pour des volumes de cette taille (cf. doc Airflow).

BashOperator plutôt que PythonOperator : les modules etl/ dépendent de
SQLAlchemy 2.0 (cohérent avec le reste du projet), incompatible avec la
version <2.0 exigée en interne par Airflow 2.10.5. Un venv dédié
(/opt/etl-venv, cf. airflow/Dockerfile) isole les deux — chaque tâche
lance ce venv en sous-processus plutôt que d'importer etl/ dans le
process Airflow lui-même.
"""
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

DAG_ID = "healthai_etl_pipeline"
ETL_PYTHON = "/opt/etl-venv/bin/python"
WORKDIR = "/opt/airflow"

with DAG(
    DAG_ID,
    start_date=datetime(2026, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["healthai", "etl"],
) as dag:

    extract_task = BashOperator(
        task_id="extract",
        bash_command=f"cd {WORKDIR} && {ETL_PYTHON} -c "
                      "'from etl.extract.extract import run; run()'",
    )

    transform_and_load_task = BashOperator(
        task_id="transform_and_load",
        bash_command=f"cd {WORKDIR} && {ETL_PYTHON} -c "
                      "'from etl.load.postgres_loader import load_data; load_data()'",
    )

    quality_check_task = BashOperator(
        task_id="quality_check",
        bash_command=f"cd {WORKDIR} && {ETL_PYTHON} -c "
                      f"'from etl.quality.checks import run_quality_checks; "
                      f"run_quality_checks(dag_id=\"{DAG_ID}\")'",
    )

    extract_task >> transform_and_load_task >> quality_check_task

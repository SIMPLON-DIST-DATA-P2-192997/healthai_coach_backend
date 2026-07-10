FROM apache/airflow:2.10.5-python3.12

USER root

# Environnement Python isolé pour les dépendances ETL (pandas, SQLAlchemy
# 2.0, psycopg2). Airflow 2.10.5 exige SQLAlchemy <2.0 en interne (cf. pip :
# "apache-airflow 2.10.5 requires sqlalchemy<2.0,>=1.4.36") — installer les
# dépendances ETL (SQLAlchemy 2.0.51, cohérent avec le reste du projet) dans
# le même environnement que le cœur d'Airflow casserait le webserver/
# scheduler. Les tâches du DAG invoquent ce venv via BashOperator plutôt que
# d'importer les modules etl/ dans le process Airflow lui-même.
RUN python -m venv /opt/etl-venv
COPY etl/requirements.txt /tmp/etl-requirements.txt
RUN /opt/etl-venv/bin/pip install --no-cache-dir -r /tmp/etl-requirements.txt \
    && chown -R airflow: /opt/etl-venv

USER airflow

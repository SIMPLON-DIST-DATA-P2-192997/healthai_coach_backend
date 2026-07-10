-- Exécuté une seule fois par l'image postgres officielle au tout premier
-- démarrage (docker-entrypoint-initdb.d), en plus de POSTGRES_DB.
-- Airflow a besoin de sa propre base pour ses métadonnées (DAG runs,
-- tâches, connexions) séparément de healthai_coach — même raisonnement
-- que 01_create_metabase_db.sql pour Metabase.
-- Le nom doit rester synchronisé avec AIRFLOW__DATABASE__SQL_ALCHEMY_CONN
-- dans .env.example.
CREATE DATABASE airflow;

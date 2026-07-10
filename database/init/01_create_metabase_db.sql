-- Exécuté une seule fois par l'image postgres officielle au tout premier
-- démarrage (docker-entrypoint-initdb.d), en plus de POSTGRES_DB.
-- Metabase a besoin de sa propre base pour stocker ses métadonnées
-- (questions, dashboards, config) séparément de healthai_coach.
-- Le nom doit rester synchronisé avec METABASE_DB_NAME dans .env.example.
CREATE DATABASE metabase;

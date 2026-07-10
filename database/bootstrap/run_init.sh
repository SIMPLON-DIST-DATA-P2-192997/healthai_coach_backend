#!/bin/sh
# Prépare une base fraîchement démarrée pour la démo/le dev : migrations,
# seed (conditionnel), puis vues KPI Metabase. Idempotent (rejouable sans
# risque) sauf le seed, qui TRUNCATE puis repeuple — jamais à exécuter sur
# de vraies données (cf. database/seed/seed_data.py).
#
# SEED_DEMO_DATA=false désactive le seed : à utiliser une fois que le vrai
# pipeline ETL (Airflow, cf. docs/guide_deploiement.md) alimente la base
# avec de vraies données, pour que db-init ne les efface plus à chaque
# `docker compose up` (cf. "Point de vigilance" dans le même guide).
set -eu

echo "== Migrations Alembic =="
alembic upgrade head

if [ "${SEED_DEMO_DATA:-true}" = "true" ]; then
  echo "== Seed de données de test =="
  python database/seed/seed_data.py
else
  echo "== SEED_DEMO_DATA=false : seed ignoré, données existantes préservées =="
fi

echo "== Vues KPI Metabase =="
psql "$DATABASE_URL" -f dashboard/kpi_queries/nutrition_biometrics.sql
psql "$DATABASE_URL" -f dashboard/kpi_queries/fitness.sql

echo "== Init terminé =="

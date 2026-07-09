#!/bin/sh
# Prépare une base fraîchement démarrée pour la démo/le dev : migrations,
# seed, puis vues KPI Metabase. Idempotent (rejouable sans risque) sauf le
# seed, qui TRUNCATE puis repeuple — jamais à exécuter sur de vraies données
# (cf. database/seed/seed_data.py).
set -eu

echo "== Migrations Alembic =="
alembic upgrade head

echo "== Seed de données de test =="
python database/seed/seed_data.py

echo "== Vues KPI Metabase =="
psql "$DATABASE_URL" -f dashboard/kpi_queries/nutrition_biometrics.sql
psql "$DATABASE_URL" -f dashboard/kpi_queries/fitness.sql

echo "== Init terminé =="

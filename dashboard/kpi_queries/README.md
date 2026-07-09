# KPI queries — Metabase

Vues SQL consommées par Metabase (Sprint 5). Toute la logique métier vit ici, pas dans Metabase — Metabase se contente d'afficher ces vues comme des tables classiques.

## Application

```bash
psql "$DATABASE_URL" -f dashboard/kpi_queries/nutrition_biometrics.sql
psql "$DATABASE_URL" -f dashboard/kpi_queries/fitness.sql
```

Toutes les vues utilisent `CREATE OR REPLACE VIEW` : rejouable sans risque après une évolution du schéma. Une fois appliquées, dans Metabase : *Admin* → *Database* → *Sync database schema now* pour qu'elles apparaissent.

## Vues disponibles

**Nutrition & biométrie** (`nutrition_biometrics.sql`)
- `vw_nutrition_meal_type_breakdown` — volume de journalisation et calories consommées par type de repas
- `vw_nutrition_top_food_items` — aliments les plus journalisés, avec calories totales
- `vw_nutrition_logs_daily` — portions et calories consommées par utilisateur et par jour
- `vw_nutrition_calories_by_category` — calories consommées agrégées par catégorie d'aliment
- `vw_biometric_trend` — relevés biométriques avec IMC calculé
- `vw_biometric_latest_per_user` — dernier relevé connu par utilisateur

**Fitness / entraînement** (`fitness.sql`)
- `vw_workout_sessions_summary` — synthèse par utilisateur (nb séances, durée, BPM)
- `vw_workout_sessions_weekly` — fréquence d'entraînement hebdomadaire
- `vw_workout_sets_by_exercise` — popularité et charge moyenne par exercice

## KPI calories (résolu — migration 35edc0b38d0b)

`food_items.calories_kcal` est exprimé pour une portion nommée (ex. *"Scrambled Eggs (2 large)"* = 180 kcal), pas pour 100 g. `serving_size_g` (jamais renseigné par aucune des 3 sources Kaggle) a été abandonné au profit de `nutrition_logs.portion_number` (décimal, ex. 1.5) : `calories_consommées = calories_kcal × portion_number`. Décision prise avec Johane/William (ETL) — voir le docstring de la migration pour le détail.

## Périmètre restant (reporté)

Qualité des données (`data_quality_log`) volontairement écarté de cette première itération : quasiment aucune donnée réelle tant qu'Airflow (Sprint 3) ne tourne pas en continu. À reprendre une fois le pipeline en place.

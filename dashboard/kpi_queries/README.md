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
- `vw_nutrition_meal_type_breakdown` — volume de journalisation par type de repas
- `vw_nutrition_top_food_items` — aliments les plus journalisés
- `vw_nutrition_logs_daily` — volume par utilisateur et par jour
- `vw_biometric_trend` — relevés biométriques avec IMC calculé
- `vw_biometric_latest_per_user` — dernier relevé connu par utilisateur

**Fitness / entraînement** (`fitness.sql`)
- `vw_workout_sessions_summary` — synthèse par utilisateur (nb séances, durée, BPM)
- `vw_workout_sessions_weekly` — fréquence d'entraînement hebdomadaire
- `vw_workout_sets_by_exercise` — popularité et charge moyenne par exercice

## Limite connue : pas de KPI calories

`food_items.calories_kcal` est exprimé pour une portion de référence (ex. *"Scrambled Eggs (2 large)"* = 180 kcal), pas pour 100 g. `serving_size_g` permettrait de ramener ça à un poids, mais n'est renseigné par aucune des 3 sources Kaggle du projet — vérifié sur les datasets complets, pas seulement les échantillons de seed. Mettre `nutrition_logs.quantity_g` à l'échelle des calories nécessiterait une hypothèse non validée (ex. "calories_kcal est pour 100g", ce qui est faux ici). Tant que cette donnée n'existe pas dans les sources, les vues nutrition s'en tiennent à `quantity_g` et à des comptages, toujours fiables.

## Périmètre restant (reporté)

Qualité des données (`data_quality_log`) volontairement écarté de cette première itération : quasiment aucune donnée réelle tant qu'Airflow (Sprint 3) ne tourne pas en continu. À reprendre une fois le pipeline en place.

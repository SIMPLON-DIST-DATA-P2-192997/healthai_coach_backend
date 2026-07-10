-- ============================================================
-- HealthAI Coach — Vues KPI Metabase : nutrition & biométrie
-- Sprint 5. Pas de logique métier dans Metabase : tout est ici.
--
-- Application : psql -f dashboard/kpi_queries/nutrition_biometrics.sql
-- (à exécuter contre la base healthai_coach ; CREATE OR REPLACE VIEW,
-- rejouable sans risque). Metabase détecte ensuite ces vues comme des
-- tables classiques via "Sync database schema now".
--
-- Calories consommées = food_items.calories_kcal * nutrition_logs.portion_number
-- (calories_kcal est exprimé pour une portion nommée, ex. "Scrambled Eggs
-- (2 large)" = 180 kcal ; portion_number est le nombre de ces portions
-- consommées, décimal, ex. 1.5). Migration 35edc0b38d0b — voir son
-- docstring pour l'historique (serving_size_g, jamais renseigné par les
-- sources Kaggle, a été abandonné au profit de ce calcul).
-- ============================================================

-- Répartition des entrées de journal par type de repas
CREATE OR REPLACE VIEW vw_nutrition_meal_type_breakdown AS
SELECT
    nl.meal_type,
    COUNT(*) AS log_count,
    COUNT(DISTINCT nl.user_id) AS distinct_users,
    ROUND(AVG(nl.portion_number), 2) AS avg_portion_number,
    ROUND(SUM(nl.portion_number * fi.calories_kcal), 1) AS total_calories_kcal,
    ROUND(AVG(nl.portion_number * fi.calories_kcal), 1) AS avg_calories_kcal
FROM nutrition_logs nl
JOIN food_items fi ON fi.food_item_id = nl.food_item_id
GROUP BY nl.meal_type
ORDER BY log_count DESC;

COMMENT ON VIEW vw_nutrition_meal_type_breakdown IS
    'Volume de journalisation et calories consommées par type de repas (breakfast/lunch/dinner/snack).';

-- Aliments les plus journalisés
CREATE OR REPLACE VIEW vw_nutrition_top_food_items AS
SELECT
    fi.food_item_id,
    fi.name,
    fi.category,
    fi.source,
    COUNT(*) AS times_logged,
    ROUND(SUM(nl.portion_number), 2) AS total_portions,
    ROUND(AVG(nl.portion_number), 2) AS avg_portion_number,
    ROUND(SUM(nl.portion_number * fi.calories_kcal), 1) AS total_calories_kcal
FROM nutrition_logs nl
JOIN food_items fi ON fi.food_item_id = nl.food_item_id
GROUP BY fi.food_item_id, fi.name, fi.category, fi.source
ORDER BY times_logged DESC;

COMMENT ON VIEW vw_nutrition_top_food_items IS
    'Aliments les plus fréquemment journalisés, par nombre d''entrées, avec calories totales consommées.';

-- Volume de journalisation et calories consommées par utilisateur et par jour
CREATE OR REPLACE VIEW vw_nutrition_logs_daily AS
SELECT
    nl.user_id,
    date_trunc('day', nl.logged_at) AS log_date,
    COUNT(*) AS entries,
    ROUND(SUM(nl.portion_number), 2) AS total_portions,
    ROUND(SUM(nl.portion_number * fi.calories_kcal), 1) AS total_calories_kcal
FROM nutrition_logs nl
JOIN food_items fi ON fi.food_item_id = nl.food_item_id
GROUP BY nl.user_id, date_trunc('day', nl.logged_at)
ORDER BY log_date, nl.user_id;

COMMENT ON VIEW vw_nutrition_logs_daily IS
    'Nombre d''entrées, portions et calories totales consommées par utilisateur et par jour.';

-- Calories consommées par catégorie d'aliment
CREATE OR REPLACE VIEW vw_nutrition_calories_by_category AS
SELECT
    COALESCE(fi.category, 'Non renseignée') AS category,
    COUNT(*) AS log_count,
    ROUND(SUM(nl.portion_number * fi.calories_kcal), 1) AS total_calories_kcal,
    ROUND(AVG(nl.portion_number * fi.calories_kcal), 1) AS avg_calories_kcal
FROM nutrition_logs nl
JOIN food_items fi ON fi.food_item_id = nl.food_item_id
GROUP BY fi.category
ORDER BY total_calories_kcal DESC;

COMMENT ON VIEW vw_nutrition_calories_by_category IS
    'Calories consommées agrégées par catégorie d''aliment (fi.category, ex. Vegetable, Meal/Processed).';

-- Relevés biométriques avec IMC calculé
CREATE OR REPLACE VIEW vw_biometric_trend AS
SELECT
    bm.measurement_id,
    bm.user_id,
    bm.measured_at,
    bm.weight_kg,
    bm.height_cm,
    ROUND(bm.weight_kg / POWER(bm.height_cm / 100.0, 2), 1) AS bmi,
    bm.body_fat_pct,
    bm.muscle_mass_kg,
    bm.resting_heart_rate,
    bm.source
FROM biometric_measurements bm
WHERE bm.height_cm IS NOT NULL AND bm.height_cm > 0;

COMMENT ON VIEW vw_biometric_trend IS
    'Relevés biométriques enrichis de l''IMC calculé (weight_kg / (height_cm/100)^2). Exclut les relevés sans taille exploitable.';

-- Dernier relevé biométrique connu par utilisateur
CREATE OR REPLACE VIEW vw_biometric_latest_per_user AS
SELECT DISTINCT ON (user_id)
    user_id,
    measured_at,
    weight_kg,
    height_cm,
    ROUND(weight_kg / POWER(height_cm / 100.0, 2), 1) AS bmi,
    body_fat_pct,
    muscle_mass_kg,
    resting_heart_rate
FROM biometric_measurements
WHERE height_cm IS NOT NULL AND height_cm > 0
ORDER BY user_id, measured_at DESC;

COMMENT ON VIEW vw_biometric_latest_per_user IS
    'Dernier relevé biométrique connu par utilisateur (1 ligne par user_id).';

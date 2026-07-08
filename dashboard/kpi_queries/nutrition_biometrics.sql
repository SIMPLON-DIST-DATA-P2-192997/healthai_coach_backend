-- ============================================================
-- HealthAI Coach — Vues KPI Metabase : nutrition & biométrie
-- Sprint 5. Pas de logique métier dans Metabase : tout est ici.
--
-- Application : psql -f dashboard/kpi_queries/nutrition_biometrics.sql
-- (à exécuter contre la base healthai_coach ; CREATE OR REPLACE VIEW,
-- rejouable sans risque). Metabase détecte ensuite ces vues comme des
-- tables classiques via "Sync database schema now".
--
-- Limite connue : pas de KPI "calories consommées". food_items.calories_kcal
-- est exprimé pour une portion de référence (ex. "Scrambled Eggs (2 large)"
-- = 180 kcal), mais serving_size_g n'est renseigné par aucune des 3 sources
-- Kaggle du projet (vérifié sur le dataset complet, pas seulement
-- l'échantillon de seed) : impossible de mettre à l'échelle sur
-- nutrition_logs.quantity_g sans inventer une hypothèse non validée. Les
-- vues ci-dessous s'en tiennent à quantity_g et à des comptages, toujours
-- fiables quelle que soit la source.
-- ============================================================

-- Répartition des entrées de journal par type de repas
CREATE OR REPLACE VIEW vw_nutrition_meal_type_breakdown AS
SELECT
    meal_type,
    COUNT(*) AS log_count,
    COUNT(DISTINCT user_id) AS distinct_users,
    ROUND(AVG(quantity_g), 1) AS avg_quantity_g
FROM nutrition_logs
GROUP BY meal_type
ORDER BY log_count DESC;

COMMENT ON VIEW vw_nutrition_meal_type_breakdown IS
    'Volume de journalisation nutrition par type de repas (breakfast/lunch/dinner/snack).';

-- Aliments les plus journalisés
CREATE OR REPLACE VIEW vw_nutrition_top_food_items AS
SELECT
    fi.food_item_id,
    fi.name,
    fi.source,
    COUNT(*) AS times_logged,
    ROUND(SUM(nl.quantity_g), 1) AS total_quantity_g,
    ROUND(AVG(nl.quantity_g), 1) AS avg_quantity_g
FROM nutrition_logs nl
JOIN food_items fi ON fi.food_item_id = nl.food_item_id
GROUP BY fi.food_item_id, fi.name, fi.source
ORDER BY times_logged DESC;

COMMENT ON VIEW vw_nutrition_top_food_items IS
    'Aliments les plus fréquemment journalisés, par nombre d''entrées.';

-- Volume de journalisation nutrition par utilisateur et par jour
CREATE OR REPLACE VIEW vw_nutrition_logs_daily AS
SELECT
    user_id,
    date_trunc('day', logged_at) AS log_date,
    COUNT(*) AS entries,
    ROUND(SUM(quantity_g), 1) AS total_quantity_g
FROM nutrition_logs
GROUP BY user_id, date_trunc('day', logged_at)
ORDER BY log_date, user_id;

COMMENT ON VIEW vw_nutrition_logs_daily IS
    'Nombre d''entrées et quantité totale journalisées (g) par utilisateur et par jour. Pas de calories (cf. limite en tête de fichier).';

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

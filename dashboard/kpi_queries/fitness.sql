-- ============================================================
-- HealthAI Coach — Vues KPI Metabase : fitness / entraînement
-- Sprint 5. Pas de logique métier dans Metabase : tout est ici.
--
-- Application : psql -f dashboard/kpi_queries/fitness.sql
-- (à exécuter contre la base healthai_coach ; CREATE OR REPLACE VIEW,
-- rejouable sans risque).
-- ============================================================

-- Synthèse des séances d'entraînement par utilisateur
CREATE OR REPLACE VIEW vw_workout_sessions_summary AS
SELECT
    user_id,
    COUNT(*) AS session_count,
    ROUND(AVG(EXTRACT(EPOCH FROM (ended_at - started_at)) / 60.0), 1) AS avg_duration_minutes,
    ROUND(AVG(max_bpm), 1) AS avg_max_bpm,
    ROUND(AVG(avg_bpm), 1) AS avg_avg_bpm,
    MIN(started_at) AS first_session_at,
    MAX(started_at) AS last_session_at
FROM workout_sessions
GROUP BY user_id;

COMMENT ON VIEW vw_workout_sessions_summary IS
    'Synthèse par utilisateur : nombre de séances, durée moyenne, BPM moyen/max, première et dernière séance.';

-- Fréquence d'entraînement hebdomadaire par utilisateur
CREATE OR REPLACE VIEW vw_workout_sessions_weekly AS
SELECT
    user_id,
    date_trunc('week', started_at) AS week_start,
    COUNT(*) AS session_count,
    ROUND(SUM(EXTRACT(EPOCH FROM (ended_at - started_at)) / 60.0), 1) AS total_duration_minutes
FROM workout_sessions
GROUP BY user_id, date_trunc('week', started_at)
ORDER BY week_start, user_id;

COMMENT ON VIEW vw_workout_sessions_weekly IS
    'Nombre de séances et durée totale (minutes) par utilisateur et par semaine ISO.';

-- Popularité et charge moyenne par exercice
CREATE OR REPLACE VIEW vw_workout_sets_by_exercise AS
SELECT
    e.exercise_id,
    e.name,
    e.body_part,
    e.target_muscle,
    e.equipment,
    COUNT(*) AS set_count,
    ROUND(AVG(ws.reps), 1) AS avg_reps,
    ROUND(AVG(ws.weight_kg), 1) AS avg_weight_kg,
    ROUND(AVG(ws.duration_seconds), 1) AS avg_duration_seconds
FROM workout_sets ws
JOIN exercises e ON e.exercise_id = ws.exercise_id
GROUP BY e.exercise_id, e.name, e.body_part, e.target_muscle, e.equipment
ORDER BY set_count DESC;

COMMENT ON VIEW vw_workout_sets_by_exercise IS
    'Popularité (nombre de séries journalisées) et moyennes (répétitions/charge/durée) par exercice.';

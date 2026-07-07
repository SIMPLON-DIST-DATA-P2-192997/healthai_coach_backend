-- ============================================================
-- HealthAI Coach — Schéma PostgreSQL (MPD)
-- Sprint 1 : traduction du MCD/MLD (cf. modele_donnees.md)
-- Statut : proposition initiale à valider par le Rôle A
-- ============================================================

CREATE TABLE users (
    user_id         SERIAL PRIMARY KEY,
    email           VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    date_of_birth   DATE,
    sex             VARCHAR(10) CHECK (sex IN ('F', 'M', 'other')),
    is_admin        BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE food_items (
    food_item_id    SERIAL PRIMARY KEY,
    external_id     VARCHAR(100),
    source          VARCHAR(50) NOT NULL,
    name            VARCHAR(255) NOT NULL,
    brand           VARCHAR(255),
    calories_kcal   NUMERIC(7,2) NOT NULL CHECK (calories_kcal >= 0),
    protein_g       NUMERIC(6,2) CHECK (protein_g >= 0),
    carbs_g         NUMERIC(6,2) CHECK (carbs_g >= 0),
    fat_g           NUMERIC(6,2) CHECK (fat_g >= 0),
    fiber_g         NUMERIC(6,2) CHECK (fiber_g >= 0),
    sugar_g         NUMERIC(6,2) CHECK (sugar_g >= 0),
    sodium_mg       NUMERIC(7,2) CHECK (sodium_mg >= 0),
    cholesterol_mg  NUMERIC(7,2) CHECK (cholesterol_mg >= 0),
    serving_size_g  NUMERIC(6,2) CHECK (serving_size_g > 0),
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source, external_id)
);

CREATE TABLE nutrition_logs (
    log_id          BIGSERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL,
    food_item_id    INTEGER NOT NULL,
    quantity_g      NUMERIC(6,2) NOT NULL CHECK (quantity_g > 0),
    meal_type       VARCHAR(20) NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    logged_at       TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_nutrition_logs_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_nutrition_logs_food_item FOREIGN KEY (food_item_id) REFERENCES food_items(food_item_id) ON DELETE RESTRICT
);

CREATE TABLE exercises (
    exercise_id     SERIAL PRIMARY KEY,
    external_id     VARCHAR(100),
    source          VARCHAR(50) NOT NULL DEFAULT 'exercisedb',
    name            VARCHAR(255) NOT NULL,
    body_part       VARCHAR(100),
    target_muscle   VARCHAR(100),
    equipment       VARCHAR(100),
    gif_url         TEXT,
    instructions    TEXT,
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source, external_id)
);

CREATE TABLE workout_sessions (
    session_id      BIGSERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL,
    started_at      TIMESTAMPTZ NOT NULL,
    ended_at        TIMESTAMPTZ,
    max_bpm         SMALLINT CHECK (max_bpm > 0),
    avg_bpm         SMALLINT CHECK (avg_bpm > 0),
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (ended_at IS NULL OR ended_at >= started_at),
    CONSTRAINT fk_workout_sessions_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE workout_sets (
    set_id           BIGSERIAL PRIMARY KEY,
    session_id       BIGINT NOT NULL,
    exercise_id      INTEGER NOT NULL,
    set_number       SMALLINT NOT NULL CHECK (set_number > 0),
    reps             SMALLINT CHECK (reps >= 0),
    weight_kg        NUMERIC(6,2) CHECK (weight_kg >= 0),
    duration_seconds INTEGER CHECK (duration_seconds >= 0),
    distance_m       NUMERIC(8,2) CHECK (distance_m >= 0),
    UNIQUE (session_id, exercise_id, set_number),
    CONSTRAINT fk_workout_sets_session FOREIGN KEY (session_id) REFERENCES workout_sessions(session_id) ON DELETE CASCADE,
    CONSTRAINT fk_workout_sets_exercise FOREIGN KEY (exercise_id) REFERENCES exercises(exercise_id) ON DELETE RESTRICT
);

CREATE TABLE biometric_measurements (
    measurement_id      BIGSERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL,
    measured_at         TIMESTAMPTZ NOT NULL,
    weight_kg           NUMERIC(5,2) CHECK (weight_kg > 0),
    height_cm           NUMERIC(5,2) CHECK (height_cm > 0),
    body_fat_pct        NUMERIC(4,2) CHECK (body_fat_pct BETWEEN 0 AND 100),
    muscle_mass_kg      NUMERIC(5,2) CHECK (muscle_mass_kg >= 0),
    resting_heart_rate  SMALLINT CHECK (resting_heart_rate > 0),
    source              VARCHAR(50) NOT NULL DEFAULT 'manual',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, measured_at),
    CONSTRAINT fk_biometric_measurements_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Historique clinique (1 utilisateur -> N relevés dans le temps, même
-- pattern que biometric_measurements)
CREATE TABLE medical_profiles (
    medical_profile_id  BIGSERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL,
    disease_type        VARCHAR(100),
    severity            VARCHAR(20) CHECK (severity IN ('Mild', 'Moderate', 'Severe')),
    cholesterol_mg_dl   NUMERIC(6,2) CHECK (cholesterol_mg_dl >= 0),
    blood_pressure_mmhg NUMERIC(5,2) CHECK (blood_pressure_mmhg >= 0),
    glucose_mg_dl       NUMERIC(6,2) CHECK (glucose_mg_dl >= 0),
    recorded_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_medical_profiles_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Préférences alimentaires déclarées (historisées pour suivre les changements)
CREATE TABLE dietary_preferences (
    dietary_preference_id  BIGSERIAL PRIMARY KEY,
    user_id                 INTEGER NOT NULL,
    dietary_restrictions    VARCHAR(255),
    allergies               VARCHAR(255),
    preferred_cuisine       VARCHAR(100),
    recorded_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_dietary_preferences_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Auto-évaluation du niveau d'activité/forme (distinct des faits mesurés
-- dans workout_sessions/workout_sets)
CREATE TABLE fitness_profiles (
    fitness_profile_id              BIGSERIAL PRIMARY KEY,
    user_id                         INTEGER NOT NULL,
    physical_activity_level         VARCHAR(20),
    workout_frequency_days_per_week SMALLINT CHECK (workout_frequency_days_per_week BETWEEN 0 AND 7),
    experience_level                VARCHAR(20),
    weekly_exercise_hours           NUMERIC(5,2) CHECK (weekly_exercise_hours >= 0),
    recorded_at                     TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_fitness_profiles_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Sortie du moteur de recommandation diététique (1 utilisateur -> N
-- recommandations générées dans le temps)
CREATE TABLE diet_recommendations (
    diet_recommendation_id           BIGSERIAL PRIMARY KEY,
    user_id                          INTEGER NOT NULL,
    daily_caloric_intake_kcal        NUMERIC(7,2) CHECK (daily_caloric_intake_kcal >= 0),
    adherence_to_diet_plan_pct       NUMERIC(5,2) CHECK (adherence_to_diet_plan_pct BETWEEN 0 AND 100),
    dietary_nutrient_imbalance_score NUMERIC(6,2),
    recommendation                   VARCHAR(50),
    recommended_at                   TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_diet_recommendations_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE data_quality_log (
    dq_log_id         BIGSERIAL PRIMARY KEY,
    source_table      VARCHAR(100) NOT NULL,
    source_record_id  VARCHAR(100),
    dag_id            VARCHAR(150),
    rule_name         VARCHAR(150) NOT NULL,
    severity          VARCHAR(20) NOT NULL CHECK (severity IN ('info', 'warning', 'error', 'critical')),
    message           TEXT NOT NULL,
    detected_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved          BOOLEAN NOT NULL DEFAULT FALSE,
    resolved_at       TIMESTAMPTZ,
    resolved_by       INTEGER,
    CONSTRAINT fk_data_quality_log_resolved_by FOREIGN KEY (resolved_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT chk_data_quality_log_resolution_consistency
        CHECK (resolved = TRUE OR (resolved_at IS NULL AND resolved_by IS NULL))
);

-- Index utiles pour les requêtes fréquentes (filtrage/tri par utilisateur + temps)
CREATE INDEX idx_nutrition_logs_user_logged_at ON nutrition_logs (user_id, logged_at);
CREATE INDEX idx_workout_sessions_user_started_at ON workout_sessions (user_id, started_at);
CREATE INDEX idx_biometric_measurements_user_measured_at ON biometric_measurements (user_id, measured_at);
CREATE INDEX idx_medical_profiles_user_recorded_at ON medical_profiles (user_id, recorded_at);
CREATE INDEX idx_dietary_preferences_user_recorded_at ON dietary_preferences (user_id, recorded_at);
CREATE INDEX idx_fitness_profiles_user_recorded_at ON fitness_profiles (user_id, recorded_at);
CREATE INDEX idx_diet_recommendations_user_recommended_at ON diet_recommendations (user_id, recommended_at);
CREATE INDEX idx_data_quality_log_unresolved ON data_quality_log (resolved) WHERE resolved = FALSE;

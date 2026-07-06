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
    serving_size_g  NUMERIC(6,2) CHECK (serving_size_g > 0),
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source, external_id)
);

CREATE TABLE nutrition_logs (
    log_id          BIGSERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    food_item_id    INTEGER NOT NULL REFERENCES food_items(food_item_id) ON DELETE RESTRICT,
    quantity_g      NUMERIC(6,2) NOT NULL CHECK (quantity_g > 0),
    meal_type       VARCHAR(20) NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    logged_at       TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
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
    user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    started_at      TIMESTAMPTZ NOT NULL,
    ended_at        TIMESTAMPTZ,
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (ended_at IS NULL OR ended_at >= started_at)
);

CREATE TABLE workout_sets (
    set_id           BIGSERIAL PRIMARY KEY,
    session_id       BIGINT NOT NULL REFERENCES workout_sessions(session_id) ON DELETE CASCADE,
    exercise_id      INTEGER NOT NULL REFERENCES exercises(exercise_id) ON DELETE RESTRICT,
    set_number       SMALLINT NOT NULL CHECK (set_number > 0),
    reps             SMALLINT CHECK (reps >= 0),
    weight_kg        NUMERIC(6,2) CHECK (weight_kg >= 0),
    duration_seconds INTEGER CHECK (duration_seconds >= 0),
    distance_m       NUMERIC(8,2) CHECK (distance_m >= 0),
    UNIQUE (session_id, exercise_id, set_number)
);

CREATE TABLE biometric_measurements (
    measurement_id      BIGSERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    measured_at         TIMESTAMPTZ NOT NULL,
    weight_kg           NUMERIC(5,2) CHECK (weight_kg > 0),
    height_cm           NUMERIC(5,2) CHECK (height_cm > 0),
    body_fat_pct        NUMERIC(4,2) CHECK (body_fat_pct BETWEEN 0 AND 100),
    muscle_mass_kg      NUMERIC(5,2) CHECK (muscle_mass_kg >= 0),
    resting_heart_rate  SMALLINT CHECK (resting_heart_rate > 0),
    source              VARCHAR(50) NOT NULL DEFAULT 'manual',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, measured_at)
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
    resolved_by       INTEGER REFERENCES users(user_id) ON DELETE SET NULL
);

-- Index utiles pour les requêtes fréquentes (filtrage/tri par utilisateur + temps)
CREATE INDEX idx_nutrition_logs_user_logged_at ON nutrition_logs (user_id, logged_at);
CREATE INDEX idx_workout_sessions_user_started_at ON workout_sessions (user_id, started_at);
CREATE INDEX idx_biometric_measurements_user_measured_at ON biometric_measurements (user_id, measured_at);
CREATE INDEX idx_data_quality_log_unresolved ON data_quality_log (resolved) WHERE resolved = FALSE;

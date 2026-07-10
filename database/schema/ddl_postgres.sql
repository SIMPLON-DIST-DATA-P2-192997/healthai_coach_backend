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

COMMENT ON TABLE users IS 'Comptes utilisateurs de l''application (coachés et administrateurs).';
COMMENT ON COLUMN users.user_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN users.email IS 'Adresse email, unique, utilisée pour l''authentification.';
COMMENT ON COLUMN users.hashed_password IS 'Mot de passe hashé (jamais stocké en clair).';
COMMENT ON COLUMN users.first_name IS 'Prénom.';
COMMENT ON COLUMN users.last_name IS 'Nom de famille.';
COMMENT ON COLUMN users.date_of_birth IS 'Date de naissance (optionnelle).';
COMMENT ON COLUMN users.sex IS 'Sexe déclaré : F, M ou other.';
COMMENT ON COLUMN users.is_admin IS 'Si vrai, l''utilisateur a les droits d''administration (accès à l''interface qualité, résolution des anomalies dans data_quality_log).';
COMMENT ON COLUMN users.created_at IS 'Date de création du compte.';
COMMENT ON COLUMN users.updated_at IS 'Date de dernière modification du compte.';

CREATE TABLE food_items (
    food_item_id    SERIAL PRIMARY KEY,
    external_id     VARCHAR(100),
    source          VARCHAR(50) NOT NULL,
    name            VARCHAR(255) NOT NULL,
    brand           VARCHAR(255),
    category        VARCHAR(50),
    calories_kcal   NUMERIC(7,2) NOT NULL CHECK (calories_kcal >= 0),
    protein_g       NUMERIC(6,2) CHECK (protein_g >= 0),
    carbs_g         NUMERIC(6,2) CHECK (carbs_g >= 0),
    fat_g           NUMERIC(6,2) CHECK (fat_g >= 0),
    fiber_g         NUMERIC(6,2) CHECK (fiber_g >= 0),
    sugar_g         NUMERIC(6,2) CHECK (sugar_g >= 0),
    sodium_mg       NUMERIC(7,2) CHECK (sodium_mg >= 0),
    cholesterol_mg  NUMERIC(7,2) CHECK (cholesterol_mg >= 0),
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source, external_id)
);

COMMENT ON TABLE food_items IS 'Catalogue des aliments et de leurs valeurs nutritionnelles, alimenté par l''ETL nutrition.';
COMMENT ON COLUMN food_items.food_item_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN food_items.external_id IS 'Identifiant de l''aliment dans la source d''origine (ex. identifiant du dataset). Combiné à `source`, sert de clé d''upsert idempotent (UNIQUE(source, external_id)) : ré-exécuter l''ETL met à jour la ligne existante au lieu de la dupliquer. Pas un champ obsolète.';
COMMENT ON COLUMN food_items.source IS 'Origine de la donnée (ex. ''kaggle_daily_food_nutrition''). Permet de tracer la provenance et de faire cohabiter plusieurs sources pour le même type de donnée sans collision (cf. UNIQUE(source, external_id)).';
COMMENT ON COLUMN food_items.name IS 'Nom de l''aliment.';
COMMENT ON COLUMN food_items.brand IS 'Marque commerciale (optionnelle).';
COMMENT ON COLUMN food_items.category IS 'Nature de l''aliment déclarée par la source (ex. ''Vegetable'', ''Meal/Processed'', ''Protein/Fish'') — taxonomie libre à deux niveaux séparés par ''/'', propre à chaque source.';
COMMENT ON COLUMN food_items.calories_kcal IS 'Apport calorique pour une portion de référence de cet aliment (kcal) — voir nutrition_logs.portion_number pour calculer les calories réellement consommées.';
COMMENT ON COLUMN food_items.protein_g IS 'Protéines (g).';
COMMENT ON COLUMN food_items.carbs_g IS 'Glucides (g).';
COMMENT ON COLUMN food_items.fat_g IS 'Lipides (g).';
COMMENT ON COLUMN food_items.fiber_g IS 'Fibres (g).';
COMMENT ON COLUMN food_items.sugar_g IS 'Sucres (g).';
COMMENT ON COLUMN food_items.sodium_mg IS 'Sodium (mg).';
COMMENT ON COLUMN food_items.cholesterol_mg IS 'Cholestérol alimentaire (mg) — à ne pas confondre avec le cholestérol sanguin de medical_profiles.cholesterol_mg_dl.';
COMMENT ON COLUMN food_items.ingested_at IS 'Date d''ingestion de la ligne par l''ETL.';

CREATE TABLE nutrition_logs (
    log_id          BIGSERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL,
    food_item_id    INTEGER NOT NULL,
    portion_number  NUMERIC(6,2) NOT NULL CHECK (portion_number > 0),
    meal_type       VARCHAR(20) NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    logged_at       TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_nutrition_logs_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_nutrition_logs_food_item FOREIGN KEY (food_item_id) REFERENCES food_items(food_item_id) ON DELETE RESTRICT
);

COMMENT ON TABLE nutrition_logs IS 'Journal des repas consommés par les utilisateurs (une ligne = un aliment consommé lors d''un repas).';
COMMENT ON COLUMN nutrition_logs.log_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN nutrition_logs.user_id IS 'Utilisateur ayant consommé l''aliment (FK users).';
COMMENT ON COLUMN nutrition_logs.food_item_id IS 'Aliment consommé (FK food_items).';
COMMENT ON COLUMN nutrition_logs.portion_number IS 'Nombre de portions consommées (peut être décimal, ex. 1.5) — à multiplier par food_items.calories_kcal pour obtenir les calories réellement consommées, la portion de référence étant déjà encodée dans le nom de l''aliment (ex. ''Scrambled Eggs (2 large)'').';
COMMENT ON COLUMN nutrition_logs.meal_type IS 'Type de repas : breakfast, lunch, dinner ou snack.';
COMMENT ON COLUMN nutrition_logs.logged_at IS 'Date/heure du repas.';
COMMENT ON COLUMN nutrition_logs.created_at IS 'Date d''enregistrement de la ligne en base.';

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

COMMENT ON TABLE exercises IS 'Catalogue des exercices physiques, alimenté par l''ETL exercises (source oss.exercisedb.dev).';
COMMENT ON COLUMN exercises.exercise_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN exercises.external_id IS 'Identifiant de l''exercice dans la source d''origine (ex. exerciseId ExerciseDB). Combiné à `source`, sert de clé d''upsert idempotent (UNIQUE(source, external_id)) : ré-exécuter l''ETL met à jour la ligne existante au lieu de la dupliquer. Pas un champ obsolète.';
COMMENT ON COLUMN exercises.source IS 'Origine de la donnée (ex. ''exercisedb'').';
COMMENT ON COLUMN exercises.name IS 'Nom de l''exercice.';
COMMENT ON COLUMN exercises.body_part IS 'Partie du corps ciblée (ex. ''back'', ''chest'').';
COMMENT ON COLUMN exercises.target_muscle IS 'Muscle principal sollicité.';
COMMENT ON COLUMN exercises.equipment IS 'Équipement nécessaire (ex. ''body weight'', ''barbell'').';
COMMENT ON COLUMN exercises.gif_url IS 'URL de l''animation/gif de démonstration.';
COMMENT ON COLUMN exercises.instructions IS 'Instructions d''exécution (une étape par ligne).';
COMMENT ON COLUMN exercises.ingested_at IS 'Date d''ingestion de la ligne par l''ETL.';

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

COMMENT ON TABLE workout_sessions IS 'Séances d''entraînement réalisées par les utilisateurs.';
COMMENT ON COLUMN workout_sessions.session_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN workout_sessions.user_id IS 'Utilisateur ayant réalisé la séance (FK users).';
COMMENT ON COLUMN workout_sessions.started_at IS 'Début de la séance.';
COMMENT ON COLUMN workout_sessions.ended_at IS 'Fin de la séance (optionnelle si en cours ou inconnue).';
COMMENT ON COLUMN workout_sessions.max_bpm IS 'Fréquence cardiaque maximale observée pendant la séance (battements/min).';
COMMENT ON COLUMN workout_sessions.avg_bpm IS 'Fréquence cardiaque moyenne observée pendant la séance (battements/min).';
COMMENT ON COLUMN workout_sessions.notes IS 'Notes libres sur la séance.';
COMMENT ON COLUMN workout_sessions.created_at IS 'Date d''enregistrement de la ligne en base.';

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

COMMENT ON TABLE workout_sets IS 'Séries d''exercices réalisées au sein d''une séance — résout l''association N,N entre workout_sessions et exercises (cf. modele_donnees.md, "Note de conception : pourquoi WORKOUT_SETS").';
COMMENT ON COLUMN workout_sets.set_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN workout_sets.session_id IS 'Séance à laquelle appartient la série (FK workout_sessions).';
COMMENT ON COLUMN workout_sets.exercise_id IS 'Exercice réalisé (FK exercises).';
COMMENT ON COLUMN workout_sets.set_number IS 'Numéro de la série au sein de la séance pour cet exercice (1, 2, 3...).';
COMMENT ON COLUMN workout_sets.reps IS 'Nombre de répétitions effectuées.';
COMMENT ON COLUMN workout_sets.weight_kg IS 'Charge utilisée (kg), si applicable.';
COMMENT ON COLUMN workout_sets.duration_seconds IS 'Durée de la série (s), pour les exercices chronométrés.';
COMMENT ON COLUMN workout_sets.distance_m IS 'Distance parcourue (m), pour les exercices de cardio/déplacement.';

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

COMMENT ON TABLE biometric_measurements IS 'Relevés biométriques des utilisateurs dans le temps (poids, taille, composition corporelle...).';
COMMENT ON COLUMN biometric_measurements.measurement_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN biometric_measurements.user_id IS 'Utilisateur concerné (FK users).';
COMMENT ON COLUMN biometric_measurements.measured_at IS 'Date/heure du relevé.';
COMMENT ON COLUMN biometric_measurements.weight_kg IS 'Poids (kg).';
COMMENT ON COLUMN biometric_measurements.height_cm IS 'Taille (cm).';
COMMENT ON COLUMN biometric_measurements.body_fat_pct IS 'Taux de masse grasse (%).';
COMMENT ON COLUMN biometric_measurements.muscle_mass_kg IS 'Masse musculaire (kg).';
COMMENT ON COLUMN biometric_measurements.resting_heart_rate IS 'Fréquence cardiaque au repos (battements/min).';
COMMENT ON COLUMN biometric_measurements.source IS 'Origine du relevé : ''manual'' (saisie utilisateur) ou nom de la source d''import (ex. ''kaggle_gym_members'').';
COMMENT ON COLUMN biometric_measurements.created_at IS 'Date d''enregistrement de la ligne en base.';

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

COMMENT ON TABLE medical_profiles IS 'Historique du profil médical déclaré par l''utilisateur (une ligne par relevé dans le temps).';
COMMENT ON COLUMN medical_profiles.medical_profile_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN medical_profiles.user_id IS 'Utilisateur concerné (FK users).';
COMMENT ON COLUMN medical_profiles.disease_type IS 'Pathologie déclarée (ex. ''Diabetes'', ''Obesity''), le cas échéant.';
COMMENT ON COLUMN medical_profiles.severity IS 'Sévérité de la pathologie : Mild, Moderate ou Severe.';
COMMENT ON COLUMN medical_profiles.cholesterol_mg_dl IS 'Cholestérol sanguin (mg/dL) — à ne pas confondre avec le cholestérol alimentaire de food_items.cholesterol_mg.';
COMMENT ON COLUMN medical_profiles.blood_pressure_mmhg IS 'Tension artérielle (mmHg), valeur unique : la source ne distingue pas systolique/diastolique (cf. modele_donnees.md).';
COMMENT ON COLUMN medical_profiles.glucose_mg_dl IS 'Glycémie (mg/dL).';
COMMENT ON COLUMN medical_profiles.recorded_at IS 'Date du relevé.';

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

COMMENT ON TABLE dietary_preferences IS 'Historique des préférences alimentaires déclarées par l''utilisateur.';
COMMENT ON COLUMN dietary_preferences.dietary_preference_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN dietary_preferences.user_id IS 'Utilisateur concerné (FK users).';
COMMENT ON COLUMN dietary_preferences.dietary_restrictions IS 'Restriction alimentaire déclarée (ex. ''Low_Sodium'', ''None'').';
COMMENT ON COLUMN dietary_preferences.allergies IS 'Allergie déclarée (ex. ''Peanuts'', ''None'').';
COMMENT ON COLUMN dietary_preferences.preferred_cuisine IS 'Type de cuisine préféré (ex. ''Mexican'').';
COMMENT ON COLUMN dietary_preferences.recorded_at IS 'Date de la déclaration.';

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

COMMENT ON TABLE fitness_profiles IS 'Auto-évaluation du niveau d''activité/forme physique de l''utilisateur dans le temps (distinct des faits mesurés dans workout_sessions/workout_sets).';
COMMENT ON COLUMN fitness_profiles.fitness_profile_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN fitness_profiles.user_id IS 'Utilisateur concerné (FK users).';
COMMENT ON COLUMN fitness_profiles.physical_activity_level IS 'Niveau d''activité physique déclaré (ex. ''Sedentary'', ''Moderate'', ''Active'').';
COMMENT ON COLUMN fitness_profiles.workout_frequency_days_per_week IS 'Fréquence d''entraînement déclarée (jours/semaine, 0 à 7).';
COMMENT ON COLUMN fitness_profiles.experience_level IS 'Niveau d''expérience sportive déclaré.';
COMMENT ON COLUMN fitness_profiles.weekly_exercise_hours IS 'Heures d''exercice hebdomadaires déclarées.';
COMMENT ON COLUMN fitness_profiles.recorded_at IS 'Date de la déclaration.';

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

COMMENT ON TABLE diet_recommendations IS 'Recommandations diététiques générées pour l''utilisateur (sortie d''un moteur de recommandation), historisées dans le temps.';
COMMENT ON COLUMN diet_recommendations.diet_recommendation_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN diet_recommendations.user_id IS 'Utilisateur concerné (FK users).';
COMMENT ON COLUMN diet_recommendations.daily_caloric_intake_kcal IS 'Apport calorique quotidien cible (kcal).';
COMMENT ON COLUMN diet_recommendations.adherence_to_diet_plan_pct IS 'Taux d''adhérence observé au plan alimentaire (%).';
COMMENT ON COLUMN diet_recommendations.dietary_nutrient_imbalance_score IS 'Score de déséquilibre nutritionnel calculé.';
COMMENT ON COLUMN diet_recommendations.recommendation IS 'Recommandation émise (ex. ''Balanced'', ''Low_Carb'', ''Low_Sodium'').';
COMMENT ON COLUMN diet_recommendations.recommended_at IS 'Date de génération de la recommandation.';

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

COMMENT ON TABLE data_quality_log IS 'Journal des anomalies de qualité détectées par l''ETL, consultées et corrigées via l''interface admin (Sprint 5).';
COMMENT ON COLUMN data_quality_log.dq_log_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN data_quality_log.source_table IS 'Table concernée par l''anomalie, en texte libre (pas de FK stricte) : doit pouvoir référencer n''importe quelle table ingérée par l''ETL sans contrainte de schéma (cf. modele_donnees.md).';
COMMENT ON COLUMN data_quality_log.source_record_id IS 'Identifiant de la ligne concernée dans la table source, si connu.';
COMMENT ON COLUMN data_quality_log.dag_id IS 'DAG Airflow ayant détecté l''anomalie (Sprint 3), si applicable.';
COMMENT ON COLUMN data_quality_log.rule_name IS 'Nom de la règle de qualité ayant déclenché l''anomalie.';
COMMENT ON COLUMN data_quality_log.severity IS 'Gravité : info, warning, error ou critical.';
COMMENT ON COLUMN data_quality_log.message IS 'Description de l''anomalie.';
COMMENT ON COLUMN data_quality_log.detected_at IS 'Date de détection.';
COMMENT ON COLUMN data_quality_log.resolved IS 'Vrai si l''anomalie a été traitée.';
COMMENT ON COLUMN data_quality_log.resolved_at IS 'Date de résolution — renseignée uniquement si resolved = TRUE (cf. contrainte chk_data_quality_log_resolution_consistency).';
COMMENT ON COLUMN data_quality_log.resolved_by IS 'Administrateur ayant résolu l''anomalie (FK users, optionnelle).';

CREATE TABLE organizations (
    organization_id  SERIAL PRIMARY KEY,
    name             VARCHAR(255) NOT NULL,
    contact_email    VARCHAR(255) NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE organizations IS 'Organisations partenaires (salles de sport, mutuelles, entreprises) pour l''offre B2B en marque blanche.';
COMMENT ON COLUMN organizations.organization_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN organizations.name IS 'Nom de l''organisation.';
COMMENT ON COLUMN organizations.contact_email IS 'Email de contact référent côté organisation.';
COMMENT ON COLUMN organizations.created_at IS 'Date de création de la fiche organisation.';

CREATE TABLE subscriptions (
    subscription_id  BIGSERIAL PRIMARY KEY,
    user_id          INTEGER NOT NULL,
    organization_id  INTEGER,
    tier             VARCHAR(20) NOT NULL CHECK (tier IN ('free', 'premium', 'premium_plus', 'b2b')),
    status           VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'expired')),
    price_eur_cents  INTEGER CHECK (price_eur_cents >= 0),
    started_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at         TIMESTAMPTZ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_subscriptions_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_subscriptions_organization FOREIGN KEY (organization_id) REFERENCES organizations(organization_id) ON DELETE RESTRICT,
    CONSTRAINT chk_subscriptions_ended_after_started CHECK (ended_at IS NULL OR ended_at >= started_at),
    CONSTRAINT chk_subscriptions_b2b_organization
        CHECK ((tier = 'b2b' AND organization_id IS NOT NULL) OR (tier <> 'b2b' AND organization_id IS NULL))
);

COMMENT ON TABLE subscriptions IS 'Historique des souscriptions des utilisateurs (free, premium, premium_plus, b2b) — cf. modele_donnees.md pour le modèle économique.';
COMMENT ON COLUMN subscriptions.subscription_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN subscriptions.user_id IS 'Utilisateur souscripteur (FK users).';
COMMENT ON COLUMN subscriptions.organization_id IS 'Organisation de rattachement B2B (FK organizations), renseignée uniquement si tier = ''b2b'' (cf. contrainte chk_subscriptions_b2b_organization).';
COMMENT ON COLUMN subscriptions.tier IS 'Palier souscrit : free, premium, premium_plus ou b2b.';
COMMENT ON COLUMN subscriptions.status IS 'Statut de la souscription : active, cancelled ou expired.';
COMMENT ON COLUMN subscriptions.price_eur_cents IS 'Prix convenu au moment de la souscription (centimes d''euro) — valeur informative, aucune intégration de paiement dans ce lot (cf. modele_donnees.md).';
COMMENT ON COLUMN subscriptions.started_at IS 'Début de la souscription.';
COMMENT ON COLUMN subscriptions.ended_at IS 'Fin de la souscription (résiliation ou changement de palier), optionnelle si toujours active.';
COMMENT ON COLUMN subscriptions.created_at IS 'Date d''enregistrement de la ligne en base.';

CREATE TABLE workout_plans (
    workout_plan_id  BIGSERIAL PRIMARY KEY,
    user_id          INTEGER NOT NULL,
    goal             VARCHAR(255),
    plan_text        TEXT NOT NULL,
    generated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_workout_plans_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

COMMENT ON TABLE workout_plans IS 'Plans d''entraînement générés par le microservice IA (palier Premium), historisés (1 utilisateur -> N plans dans le temps).';
COMMENT ON COLUMN workout_plans.workout_plan_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN workout_plans.user_id IS 'Utilisateur destinataire du plan (FK users).';
COMMENT ON COLUMN workout_plans.goal IS 'Objectif exprimé par l''utilisateur ayant motivé la génération (ex. ''perte de poids'', ''prise de masse''), si fourni.';
COMMENT ON COLUMN workout_plans.plan_text IS 'Contenu du plan généré par le microservice IA — texte libre pour l''instant (cf. modele_donnees.md, à revoir une fois le contrat du microservice connu).';
COMMENT ON COLUMN workout_plans.generated_at IS 'Date de génération du plan.';

CREATE TABLE nutrition_plans (
    nutrition_plan_id  BIGSERIAL PRIMARY KEY,
    user_id            INTEGER NOT NULL,
    goal               VARCHAR(255),
    plan_text          TEXT NOT NULL,
    generated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_nutrition_plans_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

COMMENT ON TABLE nutrition_plans IS 'Plans nutritionnels générés par le microservice IA (palier Premium), historisés (1 utilisateur -> N plans dans le temps).';
COMMENT ON COLUMN nutrition_plans.nutrition_plan_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN nutrition_plans.user_id IS 'Utilisateur destinataire du plan (FK users).';
COMMENT ON COLUMN nutrition_plans.goal IS 'Objectif exprimé par l''utilisateur ayant motivé la génération (ex. ''végétarien riche en protéines''), si fourni.';
COMMENT ON COLUMN nutrition_plans.plan_text IS 'Contenu du plan généré par le microservice IA — texte libre pour l''instant (cf. modele_donnees.md, à revoir une fois le contrat du microservice connu).';
COMMENT ON COLUMN nutrition_plans.generated_at IS 'Date de génération du plan.';

-- Index utiles pour les requêtes fréquentes (filtrage/tri par utilisateur + temps)
CREATE INDEX idx_nutrition_logs_user_logged_at ON nutrition_logs (user_id, logged_at);
CREATE INDEX idx_workout_sessions_user_started_at ON workout_sessions (user_id, started_at);
CREATE INDEX idx_biometric_measurements_user_measured_at ON biometric_measurements (user_id, measured_at);
CREATE INDEX idx_medical_profiles_user_recorded_at ON medical_profiles (user_id, recorded_at);
CREATE INDEX idx_dietary_preferences_user_recorded_at ON dietary_preferences (user_id, recorded_at);
CREATE INDEX idx_fitness_profiles_user_recorded_at ON fitness_profiles (user_id, recorded_at);
CREATE INDEX idx_diet_recommendations_user_recommended_at ON diet_recommendations (user_id, recommended_at);
CREATE INDEX idx_data_quality_log_unresolved ON data_quality_log (resolved) WHERE resolved = FALSE;
CREATE INDEX idx_subscriptions_user_started_at ON subscriptions (user_id, started_at);
CREATE UNIQUE INDEX uq_subscriptions_one_active_per_user ON subscriptions (user_id) WHERE status = 'active';
CREATE INDEX idx_workout_plans_user_generated_at ON workout_plans (user_id, generated_at);
CREATE INDEX idx_nutrition_plans_user_generated_at ON nutrition_plans (user_id, generated_at);

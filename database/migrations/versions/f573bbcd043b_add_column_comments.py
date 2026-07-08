r"""add column comments

Revision ID: f573bbcd043b
Revises: 60a90856c89f
Create Date: 2026-07-07 17:00:16.547123

Documente en base (COMMENT ON) la signification de chaque table/colonne,
suite à des questions de l'équipe sur des champs peu clairs (ex. `source`,
`external_id`). Ces commentaires sont visibles via \d+ en psql ou tout
client SQL (DBeaver, pgAdmin...), pas seulement dans ddl_postgres.sql.
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'f573bbcd043b'
down_revision: Union[str, Sequence[str], None] = '60a90856c89f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


UPGRADE_SQL = """
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
COMMENT ON TABLE food_items IS 'Catalogue des aliments et de leurs valeurs nutritionnelles, alimenté par l''ETL nutrition.';
COMMENT ON COLUMN food_items.food_item_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN food_items.external_id IS 'Identifiant de l''aliment dans la source d''origine (ex. identifiant du dataset). Combiné à `source`, sert de clé d''upsert idempotent (UNIQUE(source, external_id)) : ré-exécuter l''ETL met à jour la ligne existante au lieu de la dupliquer. Pas un champ obsolète.';
COMMENT ON COLUMN food_items.source IS 'Origine de la donnée (ex. ''kaggle_daily_food_nutrition''). Permet de tracer la provenance et de faire cohabiter plusieurs sources pour le même type de donnée sans collision (cf. UNIQUE(source, external_id)).';
COMMENT ON COLUMN food_items.name IS 'Nom de l''aliment.';
COMMENT ON COLUMN food_items.brand IS 'Marque commerciale (optionnelle).';
COMMENT ON COLUMN food_items.calories_kcal IS 'Apport calorique pour la portion de référence (kcal).';
COMMENT ON COLUMN food_items.protein_g IS 'Protéines (g).';
COMMENT ON COLUMN food_items.carbs_g IS 'Glucides (g).';
COMMENT ON COLUMN food_items.fat_g IS 'Lipides (g).';
COMMENT ON COLUMN food_items.fiber_g IS 'Fibres (g).';
COMMENT ON COLUMN food_items.sugar_g IS 'Sucres (g).';
COMMENT ON COLUMN food_items.sodium_mg IS 'Sodium (mg).';
COMMENT ON COLUMN food_items.cholesterol_mg IS 'Cholestérol alimentaire (mg) — à ne pas confondre avec le cholestérol sanguin de medical_profiles.cholesterol_mg_dl.';
COMMENT ON COLUMN food_items.serving_size_g IS 'Taille de la portion de référence (g), si connue dans la source.';
COMMENT ON COLUMN food_items.ingested_at IS 'Date d''ingestion de la ligne par l''ETL.';
COMMENT ON TABLE nutrition_logs IS 'Journal des repas consommés par les utilisateurs (une ligne = un aliment consommé lors d''un repas).';
COMMENT ON COLUMN nutrition_logs.log_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN nutrition_logs.user_id IS 'Utilisateur ayant consommé l''aliment (FK users).';
COMMENT ON COLUMN nutrition_logs.food_item_id IS 'Aliment consommé (FK food_items).';
COMMENT ON COLUMN nutrition_logs.quantity_g IS 'Quantité consommée (g).';
COMMENT ON COLUMN nutrition_logs.meal_type IS 'Type de repas : breakfast, lunch, dinner ou snack.';
COMMENT ON COLUMN nutrition_logs.logged_at IS 'Date/heure du repas.';
COMMENT ON COLUMN nutrition_logs.created_at IS 'Date d''enregistrement de la ligne en base.';
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
COMMENT ON TABLE workout_sessions IS 'Séances d''entraînement réalisées par les utilisateurs.';
COMMENT ON COLUMN workout_sessions.session_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN workout_sessions.user_id IS 'Utilisateur ayant réalisé la séance (FK users).';
COMMENT ON COLUMN workout_sessions.started_at IS 'Début de la séance.';
COMMENT ON COLUMN workout_sessions.ended_at IS 'Fin de la séance (optionnelle si en cours ou inconnue).';
COMMENT ON COLUMN workout_sessions.max_bpm IS 'Fréquence cardiaque maximale observée pendant la séance (battements/min).';
COMMENT ON COLUMN workout_sessions.avg_bpm IS 'Fréquence cardiaque moyenne observée pendant la séance (battements/min).';
COMMENT ON COLUMN workout_sessions.notes IS 'Notes libres sur la séance.';
COMMENT ON COLUMN workout_sessions.created_at IS 'Date d''enregistrement de la ligne en base.';
COMMENT ON TABLE workout_sets IS 'Séries d''exercices réalisées au sein d''une séance — résout l''association N,N entre workout_sessions et exercises (cf. modele_donnees.md, "Note de conception : pourquoi WORKOUT_SETS").';
COMMENT ON COLUMN workout_sets.set_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN workout_sets.session_id IS 'Séance à laquelle appartient la série (FK workout_sessions).';
COMMENT ON COLUMN workout_sets.exercise_id IS 'Exercice réalisé (FK exercises).';
COMMENT ON COLUMN workout_sets.set_number IS 'Numéro de la série au sein de la séance pour cet exercice (1, 2, 3...).';
COMMENT ON COLUMN workout_sets.reps IS 'Nombre de répétitions effectuées.';
COMMENT ON COLUMN workout_sets.weight_kg IS 'Charge utilisée (kg), si applicable.';
COMMENT ON COLUMN workout_sets.duration_seconds IS 'Durée de la série (s), pour les exercices chronométrés.';
COMMENT ON COLUMN workout_sets.distance_m IS 'Distance parcourue (m), pour les exercices de cardio/déplacement.';
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
COMMENT ON TABLE medical_profiles IS 'Historique du profil médical déclaré par l''utilisateur (une ligne par relevé dans le temps).';
COMMENT ON COLUMN medical_profiles.medical_profile_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN medical_profiles.user_id IS 'Utilisateur concerné (FK users).';
COMMENT ON COLUMN medical_profiles.disease_type IS 'Pathologie déclarée (ex. ''Diabetes'', ''Obesity''), le cas échéant.';
COMMENT ON COLUMN medical_profiles.severity IS 'Sévérité de la pathologie : Mild, Moderate ou Severe.';
COMMENT ON COLUMN medical_profiles.cholesterol_mg_dl IS 'Cholestérol sanguin (mg/dL) — à ne pas confondre avec le cholestérol alimentaire de food_items.cholesterol_mg.';
COMMENT ON COLUMN medical_profiles.blood_pressure_mmhg IS 'Tension artérielle (mmHg), valeur unique : la source ne distingue pas systolique/diastolique (cf. modele_donnees.md).';
COMMENT ON COLUMN medical_profiles.glucose_mg_dl IS 'Glycémie (mg/dL).';
COMMENT ON COLUMN medical_profiles.recorded_at IS 'Date du relevé.';
COMMENT ON TABLE dietary_preferences IS 'Historique des préférences alimentaires déclarées par l''utilisateur.';
COMMENT ON COLUMN dietary_preferences.dietary_preference_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN dietary_preferences.user_id IS 'Utilisateur concerné (FK users).';
COMMENT ON COLUMN dietary_preferences.dietary_restrictions IS 'Restriction alimentaire déclarée (ex. ''Low_Sodium'', ''None'').';
COMMENT ON COLUMN dietary_preferences.allergies IS 'Allergie déclarée (ex. ''Peanuts'', ''None'').';
COMMENT ON COLUMN dietary_preferences.preferred_cuisine IS 'Type de cuisine préféré (ex. ''Mexican'').';
COMMENT ON COLUMN dietary_preferences.recorded_at IS 'Date de la déclaration.';
COMMENT ON TABLE fitness_profiles IS 'Auto-évaluation du niveau d''activité/forme physique de l''utilisateur dans le temps (distinct des faits mesurés dans workout_sessions/workout_sets).';
COMMENT ON COLUMN fitness_profiles.fitness_profile_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN fitness_profiles.user_id IS 'Utilisateur concerné (FK users).';
COMMENT ON COLUMN fitness_profiles.physical_activity_level IS 'Niveau d''activité physique déclaré (ex. ''Sedentary'', ''Moderate'', ''Active'').';
COMMENT ON COLUMN fitness_profiles.workout_frequency_days_per_week IS 'Fréquence d''entraînement déclarée (jours/semaine, 0 à 7).';
COMMENT ON COLUMN fitness_profiles.experience_level IS 'Niveau d''expérience sportive déclaré.';
COMMENT ON COLUMN fitness_profiles.weekly_exercise_hours IS 'Heures d''exercice hebdomadaires déclarées.';
COMMENT ON COLUMN fitness_profiles.recorded_at IS 'Date de la déclaration.';
COMMENT ON TABLE diet_recommendations IS 'Recommandations diététiques générées pour l''utilisateur (sortie d''un moteur de recommandation), historisées dans le temps.';
COMMENT ON COLUMN diet_recommendations.diet_recommendation_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN diet_recommendations.user_id IS 'Utilisateur concerné (FK users).';
COMMENT ON COLUMN diet_recommendations.daily_caloric_intake_kcal IS 'Apport calorique quotidien cible (kcal).';
COMMENT ON COLUMN diet_recommendations.adherence_to_diet_plan_pct IS 'Taux d''adhérence observé au plan alimentaire (%).';
COMMENT ON COLUMN diet_recommendations.dietary_nutrient_imbalance_score IS 'Score de déséquilibre nutritionnel calculé.';
COMMENT ON COLUMN diet_recommendations.recommendation IS 'Recommandation émise (ex. ''Balanced'', ''Low_Carb'', ''Low_Sodium'').';
COMMENT ON COLUMN diet_recommendations.recommended_at IS 'Date de génération de la recommandation.';
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
"""

DOWNGRADE_SQL = """
COMMENT ON TABLE users IS NULL;
COMMENT ON COLUMN users.user_id IS NULL;
COMMENT ON COLUMN users.email IS NULL;
COMMENT ON COLUMN users.hashed_password IS NULL;
COMMENT ON COLUMN users.first_name IS NULL;
COMMENT ON COLUMN users.last_name IS NULL;
COMMENT ON COLUMN users.date_of_birth IS NULL;
COMMENT ON COLUMN users.sex IS NULL;
COMMENT ON COLUMN users.is_admin IS NULL;
COMMENT ON COLUMN users.created_at IS NULL;
COMMENT ON COLUMN users.updated_at IS NULL;
COMMENT ON TABLE food_items IS NULL;
COMMENT ON COLUMN food_items.food_item_id IS NULL;
COMMENT ON COLUMN food_items.external_id IS NULL;
COMMENT ON COLUMN food_items.source IS NULL;
COMMENT ON COLUMN food_items.name IS NULL;
COMMENT ON COLUMN food_items.brand IS NULL;
COMMENT ON COLUMN food_items.calories_kcal IS NULL;
COMMENT ON COLUMN food_items.protein_g IS NULL;
COMMENT ON COLUMN food_items.carbs_g IS NULL;
COMMENT ON COLUMN food_items.fat_g IS NULL;
COMMENT ON COLUMN food_items.fiber_g IS NULL;
COMMENT ON COLUMN food_items.sugar_g IS NULL;
COMMENT ON COLUMN food_items.sodium_mg IS NULL;
COMMENT ON COLUMN food_items.cholesterol_mg IS NULL;
COMMENT ON COLUMN food_items.serving_size_g IS NULL;
COMMENT ON COLUMN food_items.ingested_at IS NULL;
COMMENT ON TABLE nutrition_logs IS NULL;
COMMENT ON COLUMN nutrition_logs.log_id IS NULL;
COMMENT ON COLUMN nutrition_logs.user_id IS NULL;
COMMENT ON COLUMN nutrition_logs.food_item_id IS NULL;
COMMENT ON COLUMN nutrition_logs.quantity_g IS NULL;
COMMENT ON COLUMN nutrition_logs.meal_type IS NULL;
COMMENT ON COLUMN nutrition_logs.logged_at IS NULL;
COMMENT ON COLUMN nutrition_logs.created_at IS NULL;
COMMENT ON TABLE exercises IS NULL;
COMMENT ON COLUMN exercises.exercise_id IS NULL;
COMMENT ON COLUMN exercises.external_id IS NULL;
COMMENT ON COLUMN exercises.source IS NULL;
COMMENT ON COLUMN exercises.name IS NULL;
COMMENT ON COLUMN exercises.body_part IS NULL;
COMMENT ON COLUMN exercises.target_muscle IS NULL;
COMMENT ON COLUMN exercises.equipment IS NULL;
COMMENT ON COLUMN exercises.gif_url IS NULL;
COMMENT ON COLUMN exercises.instructions IS NULL;
COMMENT ON COLUMN exercises.ingested_at IS NULL;
COMMENT ON TABLE workout_sessions IS NULL;
COMMENT ON COLUMN workout_sessions.session_id IS NULL;
COMMENT ON COLUMN workout_sessions.user_id IS NULL;
COMMENT ON COLUMN workout_sessions.started_at IS NULL;
COMMENT ON COLUMN workout_sessions.ended_at IS NULL;
COMMENT ON COLUMN workout_sessions.max_bpm IS NULL;
COMMENT ON COLUMN workout_sessions.avg_bpm IS NULL;
COMMENT ON COLUMN workout_sessions.notes IS NULL;
COMMENT ON COLUMN workout_sessions.created_at IS NULL;
COMMENT ON TABLE workout_sets IS NULL;
COMMENT ON COLUMN workout_sets.set_id IS NULL;
COMMENT ON COLUMN workout_sets.session_id IS NULL;
COMMENT ON COLUMN workout_sets.exercise_id IS NULL;
COMMENT ON COLUMN workout_sets.set_number IS NULL;
COMMENT ON COLUMN workout_sets.reps IS NULL;
COMMENT ON COLUMN workout_sets.weight_kg IS NULL;
COMMENT ON COLUMN workout_sets.duration_seconds IS NULL;
COMMENT ON COLUMN workout_sets.distance_m IS NULL;
COMMENT ON TABLE biometric_measurements IS NULL;
COMMENT ON COLUMN biometric_measurements.measurement_id IS NULL;
COMMENT ON COLUMN biometric_measurements.user_id IS NULL;
COMMENT ON COLUMN biometric_measurements.measured_at IS NULL;
COMMENT ON COLUMN biometric_measurements.weight_kg IS NULL;
COMMENT ON COLUMN biometric_measurements.height_cm IS NULL;
COMMENT ON COLUMN biometric_measurements.body_fat_pct IS NULL;
COMMENT ON COLUMN biometric_measurements.muscle_mass_kg IS NULL;
COMMENT ON COLUMN biometric_measurements.resting_heart_rate IS NULL;
COMMENT ON COLUMN biometric_measurements.source IS NULL;
COMMENT ON COLUMN biometric_measurements.created_at IS NULL;
COMMENT ON TABLE medical_profiles IS NULL;
COMMENT ON COLUMN medical_profiles.medical_profile_id IS NULL;
COMMENT ON COLUMN medical_profiles.user_id IS NULL;
COMMENT ON COLUMN medical_profiles.disease_type IS NULL;
COMMENT ON COLUMN medical_profiles.severity IS NULL;
COMMENT ON COLUMN medical_profiles.cholesterol_mg_dl IS NULL;
COMMENT ON COLUMN medical_profiles.blood_pressure_mmhg IS NULL;
COMMENT ON COLUMN medical_profiles.glucose_mg_dl IS NULL;
COMMENT ON COLUMN medical_profiles.recorded_at IS NULL;
COMMENT ON TABLE dietary_preferences IS NULL;
COMMENT ON COLUMN dietary_preferences.dietary_preference_id IS NULL;
COMMENT ON COLUMN dietary_preferences.user_id IS NULL;
COMMENT ON COLUMN dietary_preferences.dietary_restrictions IS NULL;
COMMENT ON COLUMN dietary_preferences.allergies IS NULL;
COMMENT ON COLUMN dietary_preferences.preferred_cuisine IS NULL;
COMMENT ON COLUMN dietary_preferences.recorded_at IS NULL;
COMMENT ON TABLE fitness_profiles IS NULL;
COMMENT ON COLUMN fitness_profiles.fitness_profile_id IS NULL;
COMMENT ON COLUMN fitness_profiles.user_id IS NULL;
COMMENT ON COLUMN fitness_profiles.physical_activity_level IS NULL;
COMMENT ON COLUMN fitness_profiles.workout_frequency_days_per_week IS NULL;
COMMENT ON COLUMN fitness_profiles.experience_level IS NULL;
COMMENT ON COLUMN fitness_profiles.weekly_exercise_hours IS NULL;
COMMENT ON COLUMN fitness_profiles.recorded_at IS NULL;
COMMENT ON TABLE diet_recommendations IS NULL;
COMMENT ON COLUMN diet_recommendations.diet_recommendation_id IS NULL;
COMMENT ON COLUMN diet_recommendations.user_id IS NULL;
COMMENT ON COLUMN diet_recommendations.daily_caloric_intake_kcal IS NULL;
COMMENT ON COLUMN diet_recommendations.adherence_to_diet_plan_pct IS NULL;
COMMENT ON COLUMN diet_recommendations.dietary_nutrient_imbalance_score IS NULL;
COMMENT ON COLUMN diet_recommendations.recommendation IS NULL;
COMMENT ON COLUMN diet_recommendations.recommended_at IS NULL;
COMMENT ON TABLE data_quality_log IS NULL;
COMMENT ON COLUMN data_quality_log.dq_log_id IS NULL;
COMMENT ON COLUMN data_quality_log.source_table IS NULL;
COMMENT ON COLUMN data_quality_log.source_record_id IS NULL;
COMMENT ON COLUMN data_quality_log.dag_id IS NULL;
COMMENT ON COLUMN data_quality_log.rule_name IS NULL;
COMMENT ON COLUMN data_quality_log.severity IS NULL;
COMMENT ON COLUMN data_quality_log.message IS NULL;
COMMENT ON COLUMN data_quality_log.detected_at IS NULL;
COMMENT ON COLUMN data_quality_log.resolved IS NULL;
COMMENT ON COLUMN data_quality_log.resolved_at IS NULL;
COMMENT ON COLUMN data_quality_log.resolved_by IS NULL;
"""


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(UPGRADE_SQL)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(DOWNGRADE_SQL)

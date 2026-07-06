# HealthAI Coach — Modèle de données (MCD / MLD / MPD)

**Statut** : proposition initiale à valider par le Rôle A avant implémentation définitive (Sprint 1).
**Périmètre couvert** : utilisateurs, nutrition, exercices, biométrie, profil médical, préférences alimentaires, profil de forme, recommandations diététiques, journal de qualité des données (cf. Sprints 1, 2, 3, 4).

---

## 1. MCD (Modèle Conceptuel de Données)

```mermaid
erDiagram
    USERS ||--o{ NUTRITION_LOGS : enregistre
    FOOD_ITEMS ||--o{ NUTRITION_LOGS : "est consommé dans"
    USERS ||--o{ WORKOUT_SESSIONS : réalise
    WORKOUT_SESSIONS ||--o{ WORKOUT_SETS : contient
    EXERCISES ||--o{ WORKOUT_SETS : "est utilisé dans"
    USERS ||--o{ BIOMETRIC_MEASUREMENTS : mesure
    USERS ||--o{ MEDICAL_PROFILES : "a un historique"
    USERS ||--o{ DIETARY_PREFERENCES : déclare
    USERS ||--o{ FITNESS_PROFILES : "s'auto-évalue"
    USERS ||--o{ DIET_RECOMMENDATIONS : reçoit
    USERS ||--o{ DATA_QUALITY_LOG : "résout (optionnel)"

    USERS {
        int user_id PK
        string email
        string hashed_password
        string first_name
        string last_name
        date date_of_birth
        string sex
        bool is_admin
    }
    FOOD_ITEMS {
        int food_item_id PK
        string external_id
        string source
        string name
        string brand
        numeric calories_kcal
    }
    NUTRITION_LOGS {
        bigint log_id PK
        numeric quantity_g
        string meal_type
        timestamp logged_at
    }
    EXERCISES {
        int exercise_id PK
        string external_id
        string name
        string body_part
        string target_muscle
        string equipment
    }
    WORKOUT_SESSIONS {
        bigint session_id PK
        timestamp started_at
        timestamp ended_at
        smallint max_bpm
        smallint avg_bpm
        string notes
    }
    WORKOUT_SETS {
        bigint set_id PK
        smallint set_number
        smallint reps
        numeric weight_kg
        int duration_seconds
    }
    BIOMETRIC_MEASUREMENTS {
        bigint measurement_id PK
        timestamp measured_at
        numeric weight_kg
        numeric height_cm
        numeric body_fat_pct
    }
    MEDICAL_PROFILES {
        bigint medical_profile_id PK
        string disease_type
        string severity
        numeric cholesterol_mg_dl
        numeric blood_pressure_mmhg
        numeric glucose_mg_dl
        timestamp recorded_at
    }
    DIETARY_PREFERENCES {
        bigint dietary_preference_id PK
        string dietary_restrictions
        string allergies
        string preferred_cuisine
        timestamp recorded_at
    }
    FITNESS_PROFILES {
        bigint fitness_profile_id PK
        string physical_activity_level
        smallint workout_frequency_days_per_week
        string experience_level
        numeric weekly_exercise_hours
        timestamp recorded_at
    }
    DIET_RECOMMENDATIONS {
        bigint diet_recommendation_id PK
        numeric daily_caloric_intake_kcal
        numeric adherence_to_diet_plan_pct
        numeric dietary_nutrient_imbalance_score
        string recommendation
        timestamp recommended_at
    }
    DATA_QUALITY_LOG {
        bigint dq_log_id PK
        string source_table
        string rule_name
        string severity
        bool resolved
    }
```

### Points à valider avec le Rôle A

- Pas d'entité "coach" distincte des `USERS` (un simple flag `is_admin`) — à confirmer si un rôle coach séparé est nécessaire.
- `DATA_QUALITY_LOG` n'a volontairement pas de FK stricte vers les tables sources : elle référence `source_table` / `source_record_id` en texte libre car elle doit pouvoir logger des anomalies sur n'importe quelle table ingérée (nutrition, exercises, biometrics) sans contrainte de schéma — cf. Sprint 3.
- Une mesure biométrique par utilisateur est supposée unique par timestamp (`UNIQUE (user_id, measured_at)`) — à confirmer si plusieurs mesures le même jour (matin/soir) doivent être autorisées.
- Pas d'entité "objectifs" (goals) ni de plan nutritionnel/sportif prescrit — absent des sprints fournis, à ajouter si besoin métier confirmé.
- `MEDICAL_PROFILES`, `DIETARY_PREFERENCES`, `FITNESS_PROFILES`, `DIET_RECOMMENDATIONS` sont historisées (1 utilisateur -> N relevés dans le temps, comme `BIOMETRIC_MEASUREMENTS`) plutôt que 1-1, pour garder l'historique des changements — à confirmer que c'est le bon choix plutôt qu'un profil unique mis à jour en place.
- `blood_pressure_mmhg` est stocké comme une valeur unique (le dataset source ne distingue pas systolique/diastolique) — à revoir si une vraie mesure tensionnelle (deux valeurs) est nécessaire.

---

## 2. MLD (Modèle Logique de Données)

Notation Merise : `#` préfixe une clé étrangère.

```
USERS (user_id, email, hashed_password, first_name, last_name, date_of_birth, sex, is_admin, created_at, updated_at)

FOOD_ITEMS (food_item_id, external_id, source, name, brand, calories_kcal, protein_g, carbs_g, fat_g, fiber_g, sugar_g, sodium_mg, cholesterol_mg, serving_size_g, ingested_at)

NUTRITION_LOGS (log_id, #user_id, #food_item_id, quantity_g, meal_type, logged_at, created_at)

EXERCISES (exercise_id, external_id, source, name, body_part, target_muscle, equipment, gif_url, instructions, ingested_at)

WORKOUT_SESSIONS (session_id, #user_id, started_at, ended_at, max_bpm, avg_bpm, notes, created_at)

WORKOUT_SETS (set_id, #session_id, #exercise_id, set_number, reps, weight_kg, duration_seconds, distance_m)

BIOMETRIC_MEASUREMENTS (measurement_id, #user_id, measured_at, weight_kg, height_cm, body_fat_pct, muscle_mass_kg, resting_heart_rate, source, created_at)

MEDICAL_PROFILES (medical_profile_id, #user_id, disease_type, severity, cholesterol_mg_dl, blood_pressure_mmhg, glucose_mg_dl, recorded_at)

DIETARY_PREFERENCES (dietary_preference_id, #user_id, dietary_restrictions, allergies, preferred_cuisine, recorded_at)

FITNESS_PROFILES (fitness_profile_id, #user_id, physical_activity_level, workout_frequency_days_per_week, experience_level, weekly_exercise_hours, recorded_at)

DIET_RECOMMENDATIONS (diet_recommendation_id, #user_id, daily_caloric_intake_kcal, adherence_to_diet_plan_pct, dietary_nutrient_imbalance_score, recommendation, recommended_at)

DATA_QUALITY_LOG (dq_log_id, source_table, source_record_id, dag_id, rule_name, severity, message, detected_at, resolved, resolved_at, #resolved_by)
```

Toutes les associations du MCD sont de cardinalité 1,N côté "possède/contient" — aucune table associative n'est nécessaire, chaque FK est absorbée côté table "N".

---

## 3. MPD (Modèle Physique de Données)

Traduit en PostgreSQL dans [`ddl_postgres.sql`](./ddl_postgres.sql) : types précis, contraintes `CHECK`, `NOT NULL`, `UNIQUE`, `ON DELETE`, et index sur les colonnes de filtrage/tri fréquents (`user_id` + colonne temporelle sur chaque table de journal).

## Import dans drawdb

Le fichier `ddl_postgres.sql` peut être importé directement dans [drawdb](https://drawdb.app) via *Import → SQL* pour obtenir le diagramme visuel.

# Seed de données de test — Sprint 1

**Usage dev/test uniquement.** `seed_data.py` vide (`TRUNCATE ... CASCADE`) puis repeuple les tables — ne jamais l'exécuter sur un environnement avec de vraies données.

```bash
pip install -r database/seed/requirements.txt
DATABASE_URL=postgresql://user:pass@host:5432/db python database/seed/seed_data.py
```

## Origine des données

Échantillons de 50 lignes (`database/seed/fixtures/*.csv`) extraits de 3 datasets Kaggle publics, pour ne pas dépendre d'identifiants Kaggle au moment du seed :

- [`diet-recommendations-dataset`](https://www.kaggle.com/datasets/ziya07/diet-recommendations-dataset) (ziya07)
- [`gym-members-exercise-dataset`](https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset) (valakhorasani)
- [`daily-food-and-nutrition-dataset`](https://www.kaggle.com/datasets/adilshamim8/daily-food-and-nutrition-dataset) (adilshamim8)

**Important** : ces 3 datasets sont des **snapshots/catalogues plats** (aucun `user_id`, aucune date pour 2 des 3), pas des journaux d'activité par utilisateur. Ils servent uniquement à peupler des données de test réalistes ; le modèle applicatif (`nutrition_logs`, `workout_sessions`, etc.) reste celui défini dans [`modele_donnees.md`](./modele_donnees.md).

## Mapping colonnes -> tables

### `daily_food_nutrition_sample.csv` -> `food_items`
Correspondance directe : `Calories (kcal)`, `Protein (g)`, `Carbohydrates (g)`, `Fat (g)`, `Fiber (g)`, `Sugars (g)`, `Sodium (mg)`, `Cholesterol (mg)` (colonne ajoutée au schéma pour cette raison).
**Non utilisées** : `Category`, `Meal_Type`, `Water_Intake (ml)` — attributs de l'aliment sans équivalent dans `food_items` (Meal_Type y est une catégorie usuelle du produit, pas un événement de consommation).

### `diet_recommendations_sample.csv` -> `users` + `biometric_measurements`
Un utilisateur synthétique par `Patient_ID` (email `<patient_id>@seed.local`, `date_of_birth` dérivée de `Age`), une mesure biométrique (`Weight_kg`, `Height_cm`).
**Non utilisées** (aucune table actuelle ne les couvre) : `Disease_Type`, `Severity`, `Physical_Activity_Level`, `Daily_Caloric_Intake`, `Cholesterol_mg/dL` (cholestérol sanguin, à ne pas confondre avec celui des aliments), `Blood_Pressure_mmHg`, `Glucose_mg/dL`, `Dietary_Restrictions`, `Allergies`, `Preferred_Cuisine`, `Weekly_Exercise_Hours`, `Adherence_to_Diet_Plan`, `Dietary_Nutrient_Imbalance_Score`, `Diet_Recommendation`.

### `gym_members_exercise_sample.csv` -> `users` + `biometric_measurements` + `exercises` + `workout_sessions` + `workout_sets`
Un utilisateur synthétique par ligne, une mesure biométrique (`Weight (kg)`, `Height (m)` convertie en cm, `Fat_Percentage`, `Resting_BPM`), une session (`Session_Duration (hours)` -> `started_at`/`ended_at`, le reste en `notes`), un set unique par session référençant l'exercice correspondant à `Workout_Type` (catalogue `exercises` peuplé à partir des valeurs distinctes de cette colonne).
**Non utilisées** : `Max_BPM`, `Avg_BPM`, `Workout_Frequency (days/week)`, `Experience_Level` (repris en texte libre dans `notes`, pas de colonne dédiée).

### Données illustratives (sans source Kaggle)
- `nutrition_logs` : 2 entrées par utilisateur synthétique (10 premiers), aliment et quantité aléatoires — juste pour démontrer la relation `users` <-> `food_items`, ne pas interpréter comme des repas réels.
- `data_quality_log` : 3 lignes d'exemple illustrant le format attendu (utile pour tester l'interface admin Gradio du Sprint 5).

## Point de qualité de données rencontré

Le fichier `daily-food-and-nutrition-dataset` contient des virgules non échappées dans `Food_Item` (ex. `Milk (2%, 1 cup)`, `Tea (Green, 1 cup)`), qui décalent les colonnes suivantes en CSV naïf. `read_csv()` dans `seed_data.py` détecte les lignes avec un nombre de champs excédentaire et les refusionne dans la 1re colonne. À reproduire dans `etl/transform/clean_nutrition.py` au Sprint 2.

## Ouvert à discussion avec le Rôle A

Les datasets `diet-recommendations` et une partie de `gym-members` contiennent des informations riches (profil médical, préférences alimentaires, recommandation de régime) qui n'ont actuellement aucune table cible. À évaluer : faut-il une table `dietary_preferences` / `medical_profile` pour exploiter ces données au-delà du seed ?

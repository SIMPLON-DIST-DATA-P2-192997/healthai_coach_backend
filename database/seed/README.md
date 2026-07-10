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

### Récupérer les datasets complets (au-delà des échantillons de 50 lignes)

Nécessaire pour l'ETL du Sprint 2 (`etl/extract/`), pas pour lancer le seed (les échantillons dans `fixtures/` suffisent).

1. Créer un compte sur [kaggle.com](https://www.kaggle.com) si besoin.
2. Générer un token API : *Account* (menu avatar en haut à droite) → *Settings* → section *API* → **Create New Token**. Ça télécharge un fichier `kaggle.json` contenant `{"username": "...", "key": "..."}`.
3. Placer ce fichier à l'emplacement attendu par le CLI, avec des droits restreints :
   ```bash
   mkdir -p ~/.kaggle
   mv ~/Téléchargements/kaggle.json ~/.kaggle/kaggle.json
   chmod 600 ~/.kaggle/kaggle.json
   ```
4. Installer le CLI dans un environnement isolé (les systèmes récents refusent le `pip install` global — PEP 668) :
   ```bash
   python3 -m venv .venv-kaggle
   source .venv-kaggle/bin/activate
   pip install kaggle
   kaggle --version
   ```
   Alternative avec [pipx](https://pipx.pypa.io/) (plus adapté pour un outil en ligne de commande) : `pipx install kaggle`.
5. Télécharger un dataset :
   ```bash
   kaggle datasets download -d ziya07/diet-recommendations-dataset --unzip -p chemin/de/sortie
   ```

## Mapping colonnes -> tables

### `daily_food_nutrition_sample.csv` -> `food_items`
Correspondance directe : `Calories (kcal)`, `Protein (g)`, `Carbohydrates (g)`, `Fat (g)`, `Fiber (g)`, `Sugars (g)`, `Sodium (mg)`, `Cholesterol (mg)`, `Category` -> `category` (colonnes ajoutées au schéma pour cette raison).
**Non utilisées** : `Meal_Type`, `Water_Intake (ml)` — attributs de l'aliment sans équivalent dans `food_items` (Meal_Type y est une catégorie usuelle du produit, pas un événement de consommation).

### `diet_recommendations_sample.csv` -> `users` + `biometric_measurements` + `medical_profiles` + `dietary_preferences` + `fitness_profiles` + `diet_recommendations`
Un utilisateur synthétique par `Patient_ID` (email `<patient_id>@seed.local`, `date_of_birth` dérivée de `Age`) :
- `biometric_measurements` : `Weight_kg`, `Height_cm`
- `medical_profiles` : `Disease_Type`, `Severity`, `Cholesterol_mg/dL` (cholestérol **sanguin**, à ne pas confondre avec celui des aliments), `Blood_Pressure_mmHg` (valeur unique, le dataset ne distingue pas systolique/diastolique), `Glucose_mg/dL`
- `dietary_preferences` : `Dietary_Restrictions`, `Allergies`, `Preferred_Cuisine`
- `fitness_profiles` : `Physical_Activity_Level`, `Weekly_Exercise_Hours`
- `diet_recommendations` : `Daily_Caloric_Intake`, `Adherence_to_Diet_Plan`, `Dietary_Nutrient_Imbalance_Score`, `Diet_Recommendation`

Toutes ces tables sont historisées (`recorded_at`/`recommended_at`) : un même utilisateur peut avoir plusieurs relevés dans le temps, comme `biometric_measurements`.

### `gym_members_exercise_sample.csv` -> `users` + `biometric_measurements` + `exercises` + `workout_sessions` + `workout_sets` + `fitness_profiles`
Un utilisateur synthétique par ligne, une mesure biométrique (`Weight (kg)`, `Height (m)` convertie en cm, `Fat_Percentage`, `Resting_BPM`), une session (`Session_Duration (hours)` -> `started_at`/`ended_at`, `Max_BPM`/`Avg_BPM`, le reste en `notes`), un set unique par session référençant l'exercice correspondant à `Workout_Type` (catalogue `exercises` peuplé à partir des valeurs distinctes de cette colonne), et un profil de forme (`fitness_profiles` : `Workout_Frequency (days/week)`, `Experience_Level`).

### Données illustratives (sans source Kaggle)
- `nutrition_logs` : 2 entrées par utilisateur synthétique (10 premiers), aliment et nombre de portions aléatoires — juste pour démontrer la relation `users` <-> `food_items`, ne pas interpréter comme des repas réels.
- `data_quality_log` : 3 lignes d'exemple illustrant le format attendu (utile pour tester l'interface admin Gradio du Sprint 5).

## Point de qualité de données rencontré

Le fichier `daily-food-and-nutrition-dataset` contient des virgules non échappées dans `Food_Item` (ex. `Milk (2%, 1 cup)`, `Tea (Green, 1 cup)`), qui décalent les colonnes suivantes en CSV naïf. `read_csv()` dans `seed_data.py` détecte les lignes avec un nombre de champs excédentaire et les refusionne dans la 1re colonne. À reproduire dans `etl/transform/clean_nutrition.py` au Sprint 2.

## Historique : extension du schéma pour couvrir les données riches

Les datasets `diet-recommendations` et `gym-members` contenaient des informations (profil médical, préférences alimentaires, recommandation de régime, profil de forme) qui n'avaient initialement aucune table cible. Décision (Rôle A) : les capter plutôt que les ignorer, car ce sont exactement les données attendues par les clients d'une appli de coaching santé. D'où l'ajout de `medical_profiles`, `dietary_preferences`, `fitness_profiles`, `diet_recommendations` (cf. [`modele_donnees.md`](./modele_donnees.md)) et des colonnes `max_bpm`/`avg_bpm` sur `workout_sessions`.

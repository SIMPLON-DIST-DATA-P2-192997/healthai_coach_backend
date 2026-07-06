"""Seed minimal de données de test (Sprint 1).

ATTENTION : usage dev/test uniquement. Ce script vide (TRUNCATE ... CASCADE)
puis repeuple les tables avant de les repeupler — ne jamais l'exécuter sur
un environnement contenant de vraies données utilisateur.

Sources (échantillons de 50 lignes committés dans fixtures/, cf.
database/seed/README.md pour le mapping colonnes -> tables et les
hypothèses prises) :
- daily_food_nutrition_sample.csv    -> food_items
- diet_recommendations_sample.csv    -> users + biometric_measurements
- gym_members_exercise_sample.csv    -> users + biometric_measurements
                                         + exercises + workout_sessions

Usage :
    DATABASE_URL=postgresql://user:pass@host:5432/db python seed_data.py
"""

import csv
import os
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg2

FIXTURES_DIR = Path(__file__).parent / "fixtures"
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://healthai:changeme@localhost:5432/healthai_coach"
)


def read_csv(filename):
    """Lit un CSV en tolérant les virgules non échappées dans la 1re colonne.

    Le dataset source contient des noms d'aliments avec virgule libre non
    quotée (ex. "Milk (2%, 1 cup)"), ce qui décale les colonnes suivantes.
    On fusionne les champs en trop dans la 1re colonne plutôt que de
    planter ou de perdre silencieusement la ligne.
    """
    with open(FIXTURES_DIR / filename, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        n = len(header)
        rows = []
        for raw in reader:
            if len(raw) > n:
                excess = len(raw) - n
                raw = [",".join(raw[: excess + 1])] + raw[excess + 1 :]
            rows.append(dict(zip(header, raw)))
        return rows


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def truncate_all(cur):
    cur.execute(
        """
        TRUNCATE TABLE
            data_quality_log, workout_sets, workout_sessions,
            biometric_measurements, nutrition_logs, exercises,
            food_items, users
        RESTART IDENTITY CASCADE
        """
    )


def seed_food_items(cur):
    rows = read_csv("daily_food_nutrition_sample.csv")
    food_item_ids = []
    for i, row in enumerate(rows):
        cur.execute(
            """
            INSERT INTO food_items
                (external_id, source, name, calories_kcal, protein_g, carbs_g,
                 fat_g, fiber_g, sugar_g, sodium_mg, cholesterol_mg)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING food_item_id
            """,
            (
                str(i),
                "kaggle_daily_food_nutrition",
                row["Food_Item"],
                to_float(row["Calories (kcal)"]),
                to_float(row["Protein (g)"]),
                to_float(row["Carbohydrates (g)"]),
                to_float(row["Fat (g)"]),
                to_float(row["Fiber (g)"]),
                to_float(row["Sugars (g)"]),
                to_float(row["Sodium (mg)"]),
                to_float(row["Cholesterol (mg)"]),
            ),
        )
        food_item_ids.append(cur.fetchone()[0])
    print(f"food_items : {len(food_item_ids)} lignes")
    return food_item_ids


def seed_exercises(cur, gym_rows):
    workout_types = sorted({row["Workout_Type"] for row in gym_rows})
    exercise_ids = {}
    for name in workout_types:
        cur.execute(
            """
            INSERT INTO exercises (external_id, source, name)
            VALUES (%s, %s, %s)
            RETURNING exercise_id
            """,
            (name.lower(), "kaggle_gym_members", name),
        )
        exercise_ids[name] = cur.fetchone()[0]
    print(f"exercises : {len(exercise_ids)} lignes")
    return exercise_ids


SEX_MAP = {"Male": "M", "Female": "F"}


def seed_diet_recommendations_users(cur):
    rows = read_csv("diet_recommendations_sample.csv")
    now = datetime.now(timezone.utc)
    user_ids = []
    for row in rows:
        age = int(float(row["Age"]))
        dob = (now - timedelta(days=age * 365)).date()
        cur.execute(
            """
            INSERT INTO users (email, hashed_password, first_name, last_name, date_of_birth, sex)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING user_id
            """,
            (
                f"{row['Patient_ID'].lower()}@seed.local",
                "seed-not-a-real-hash",
                "Patient",
                row["Patient_ID"],
                dob,
                SEX_MAP.get(row["Gender"], "other"),
            ),
        )
        user_id = cur.fetchone()[0]
        user_ids.append(user_id)

        cur.execute(
            """
            INSERT INTO biometric_measurements (user_id, measured_at, weight_kg, height_cm, source)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (user_id, now, to_float(row["Weight_kg"]), to_float(row["Height_cm"]), "kaggle_diet_recommendations"),
        )
    print(f"users (diet_recommendations) : {len(user_ids)} lignes")
    return user_ids


def seed_gym_members_users_and_sessions(cur, gym_rows, exercise_ids):
    now = datetime.now(timezone.utc)
    user_ids = []
    for i, row in enumerate(gym_rows):
        age = int(float(row["Age"]))
        dob = (now - timedelta(days=age * 365)).date()
        cur.execute(
            """
            INSERT INTO users (email, hashed_password, first_name, last_name, date_of_birth, sex)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING user_id
            """,
            (
                f"gymmember{i}@seed.local",
                "seed-not-a-real-hash",
                "Gym",
                f"Member{i}",
                dob,
                SEX_MAP.get(row["Gender"], "other"),
            ),
        )
        user_id = cur.fetchone()[0]
        user_ids.append(user_id)

        height_cm = to_float(row["Height (m)"]) * 100 if row["Height (m)"] else None
        cur.execute(
            """
            INSERT INTO biometric_measurements
                (user_id, measured_at, weight_kg, height_cm, body_fat_pct, resting_heart_rate, source)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                now,
                to_float(row["Weight (kg)"]),
                height_cm,
                to_float(row["Fat_Percentage"]),
                int(float(row["Resting_BPM"])) if row["Resting_BPM"] else None,
                "kaggle_gym_members",
            ),
        )

        duration_hours = to_float(row["Session_Duration (hours)"]) or 0
        started_at = now - timedelta(days=random.randint(1, 30))
        ended_at = started_at + timedelta(hours=duration_hours)
        cur.execute(
            """
            INSERT INTO workout_sessions (user_id, started_at, ended_at, notes)
            VALUES (%s, %s, %s, %s)
            RETURNING session_id
            """,
            (
                user_id,
                started_at,
                ended_at,
                f"Workout_Type={row['Workout_Type']}; Calories_Burned={row['Calories_Burned']}; "
                f"Experience_Level={row['Experience_Level']}",
            ),
        )
        session_id = cur.fetchone()[0]

        cur.execute(
            """
            INSERT INTO workout_sets (session_id, exercise_id, set_number, duration_seconds)
            VALUES (%s, %s, %s, %s)
            """,
            (session_id, exercise_ids[row["Workout_Type"]], 1, int(duration_hours * 3600)),
        )
    print(f"users (gym_members) + workout_sessions/sets : {len(user_ids)} lignes")
    return user_ids


def seed_illustrative_nutrition_logs(cur, user_ids, food_item_ids):
    now = datetime.now(timezone.utc)
    meal_types = ["breakfast", "lunch", "dinner", "snack"]
    count = 0
    for user_id in user_ids[:10]:
        for _ in range(2):
            cur.execute(
                """
                INSERT INTO nutrition_logs (user_id, food_item_id, quantity_g, meal_type, logged_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    random.choice(food_item_ids),
                    round(random.uniform(50, 300), 1),
                    random.choice(meal_types),
                    now - timedelta(days=random.randint(0, 7)),
                ),
            )
            count += 1
    print(f"nutrition_logs (illustratif) : {count} lignes")


def seed_data_quality_log(cur):
    examples = [
        ("food_items", None, "check_negative_values", "warning",
         "Valeur négative détectée sur une colonne nutritionnelle avant nettoyage."),
        ("nutrition_logs", None, "check_fk_integrity", "error",
         "food_item_id introuvable dans food_items au moment de l'ingestion."),
        ("biometric_measurements", None, "check_range", "info",
         "body_fat_pct hors de la plage 0-100, ligne écartée."),
    ]
    for source_table, source_record_id, rule_name, severity, message in examples:
        cur.execute(
            """
            INSERT INTO data_quality_log (source_table, source_record_id, rule_name, severity, message)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (source_table, source_record_id, rule_name, severity, message),
        )
    print(f"data_quality_log (illustratif) : {len(examples)} lignes")


def main():
    gym_rows = read_csv("gym_members_exercise_sample.csv")

    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn:
            with conn.cursor() as cur:
                truncate_all(cur)
                food_item_ids = seed_food_items(cur)
                exercise_ids = seed_exercises(cur, gym_rows)
                diet_user_ids = seed_diet_recommendations_users(cur)
                gym_user_ids = seed_gym_members_users_and_sessions(cur, gym_rows, exercise_ids)
                seed_illustrative_nutrition_logs(cur, diet_user_ids + gym_user_ids, food_item_ids)
                seed_data_quality_log(cur)
        print("Seed terminé avec succès.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

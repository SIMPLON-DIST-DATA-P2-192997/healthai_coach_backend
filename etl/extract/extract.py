import json
import os

import pandas as pd
import requests
from ratelimit import limits, sleep_and_retry

DATA_PATH = "./etl/data"

KAGGLE_DATASETS = [
    {
        "name": "nutrition.csv",
        "url": "https://www.kaggle.com/api/v1/datasets/download/adilshamim8/daily-food-and-nutrition-dataset",
    },
    {
        "name": "diet.csv",
        "url": "https://www.kaggle.com/api/v1/datasets/download/ziya07/diet-recommendations-dataset",
    },
    {
        "name": "user.csv",
        "url": "https://www.kaggle.com/api/v1/datasets/download/valakhorasani/gym-members-exercise-dataset",
    },
    {
        "name": "activity.csv",
        "url": "https://www.kaggle.com/api/v1/datasets/download/nadeemajeedch/fitness-tracker-dataset",
    },
]

EXERCISEDB_URL = "https://oss.exercisedb.dev/api/v1/exercises"


@sleep_and_retry
@limits(calls=1, period=1)
def fetch_exercises_page(after: str | None = None, limit: int = 25) -> dict:
    """Récupère une page d'exercices depuis ExerciseDB (pagination par `after`,
    cf. tests/etl/test_mocking_example.py pour le contrat de l'API)."""
    params = {"limit": limit}
    if after:
        params["after"] = after
    response = requests.get(EXERCISEDB_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def extract_kaggle_datasets() -> None:
    """Télécharge les 4 jeux de données Kaggle vers etl/data/ (bruts, sans transformation)."""
    os.makedirs(DATA_PATH, exist_ok=True)
    for item in KAGGLE_DATASETS:
        df = pd.read_csv(item["url"], compression="zip", on_bad_lines="skip")
        df.to_csv(f"{DATA_PATH}/{item['name']}")


def extract_exercises() -> None:
    """Pagine l'intégralité du catalogue ExerciseDB vers etl/data/exercicesAPI.json."""
    os.makedirs(DATA_PATH, exist_ok=True)

    page = fetch_exercises_page()
    exercises = page["data"]
    has_next_page = page["meta"]["hasNextPage"]
    next_cursor = page["meta"].get("nextCursor")

    while has_next_page:
        print(f"Récupération de la page suivante (curseur: {next_cursor})...")
        try:
            page = fetch_exercises_page(after=next_cursor)
        except requests.HTTPError as exc:
            print(f"\n[!] L'API a bloqué. {exc}")
            break

        exercises.extend(page["data"])
        has_next_page = page["meta"]["hasNextPage"]
        next_cursor = page["meta"].get("nextCursor")

    with open(f"{DATA_PATH}/exercicesAPI.json", mode="w", encoding="utf-8") as file:
        json.dump(exercises, file, indent=4, ensure_ascii=False)


def run() -> None:
    """Point d'entrée extraction : différé dans une fonction (pas exécuté à
    l'import) pour un usage sûr depuis Airflow — cf. etl/load/postgres_loader.py
    pour la même convention côté chargement."""
    extract_kaggle_datasets()
    extract_exercises()


if __name__ == "__main__":
    run()

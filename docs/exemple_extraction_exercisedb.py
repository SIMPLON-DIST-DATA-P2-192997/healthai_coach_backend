"""EXEMPLE (à adapter par l'équipe ETL) — extraction + chargement du catalogue d'exercices.

Ce script n'est PAS le livrable du Sprint 2 : l'ETL réel (etl/extract/,
etl/transform/, etl/load/) reste sous la responsabilité de l'équipe qui
travaille sur le module exercises. C'est une démonstration bout en bout,
volontairement placée dans docs/, pour :

1. Prouver que l'extraction fonctionne réellement. Source retenue :
   oss.exercisedb.dev (API gratuite, sans clé, 1500 exercices). Pagination
   via le paramètre `after=<exerciseId>` (valeur prise dans meta.nextCursor
   de la réponse précédente) — attention, `nextCursor`, `offset`, `page` et
   un `limit` élevé sont silencieusement ignorés par l'API (confirmé via la
   spec OpenAPI /swagger) ; `limit` est plafonné à 25 par requête, d'où la
   boucle de pagination ci-dessous. Voir database/schema/modele_donnees.md
   pour le détail de cette vérification.
2. Montrer comment peupler exercises + exercise_secondary_muscles à partir
   de champs qui se présentent comme des tableaux côté API mais sont en
   réalité mono-valués (sauf secondaryMuscles, vérifié sur les 1500
   exercices réels).

Usage :
    pip install psycopg2-binary
    DATABASE_URL=postgresql://user:pass@host:5432/db python docs/exemple_extraction_exercisedb.py
"""

import json
import os
import time
import urllib.request

import psycopg2

API_URL = "https://oss.exercisedb.dev/api/v1/exercises"
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://healthai:changeme@localhost:5432/healthai_coach"
)


def extract():
    """Parcourt toutes les pages via le paramètre `after` (le seul qui
    fonctionne réellement pour paginer cette API)."""
    all_exercises = []
    after = None
    while True:
        url = f"{API_URL}?limit=25" + (f"&after={after}" if after else "")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.load(resp)
        all_exercises.extend(data["data"])
        if not data["meta"]["hasNextPage"]:
            break
        after = data["meta"]["nextCursor"]
        time.sleep(1.2)  # l'API rate-limite les appels trop rapprochés (HTTP 429)
    return all_exercises


def transform(raw_exercises):
    """Convertit chaque exercice brut en (ligne exercises, muscles secondaires).

    bodyParts/equipments/targetMuscles sont toujours de longueur 1 dans les
    données réelles (vérifié sur les 1500 exercices) -> on prend le premier
    élément sans perte d'info. secondaryMuscles varie réellement de 0 à 10
    -> table de jointure dédiée.
    """
    rows = []
    for ex in raw_exercises:
        body_parts = ex.get("bodyParts") or []
        equipments = ex.get("equipments") or []
        target_muscles = ex.get("targetMuscles") or []
        exercise_row = {
            "external_id": ex["exerciseId"],
            "source": "exercisedb",
            "name": ex["name"],
            "body_part": body_parts[0] if body_parts else None,
            "equipment": equipments[0] if equipments else None,
            "target_muscle": target_muscles[0] if target_muscles else None,
            "gif_url": ex.get("gifUrl"),
            "instructions": "\n".join(ex.get("instructions") or []),
        }
        rows.append((exercise_row, ex.get("secondaryMuscles") or []))
    return rows


def load(rows):
    """Upsert sur (source, external_id) — cf. contrainte UNIQUE de la table."""
    conn = psycopg2.connect(DATABASE_URL)
    inserted = 0
    with conn, conn.cursor() as cur:
        for exercise_row, secondary_muscles in rows:
            cur.execute(
                """
                INSERT INTO exercises
                    (external_id, source, name, body_part, equipment, target_muscle, gif_url, instructions)
                VALUES (%(external_id)s, %(source)s, %(name)s, %(body_part)s, %(equipment)s,
                        %(target_muscle)s, %(gif_url)s, %(instructions)s)
                ON CONFLICT (source, external_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    body_part = EXCLUDED.body_part,
                    equipment = EXCLUDED.equipment,
                    target_muscle = EXCLUDED.target_muscle,
                    gif_url = EXCLUDED.gif_url,
                    instructions = EXCLUDED.instructions
                RETURNING exercise_id
                """,
                exercise_row,
            )
            exercise_id = cur.fetchone()[0]
            cur.execute("DELETE FROM exercise_secondary_muscles WHERE exercise_id = %s", (exercise_id,))
            for muscle in secondary_muscles:
                cur.execute(
                    "INSERT INTO exercise_secondary_muscles (exercise_id, muscle) VALUES (%s, %s) "
                    "ON CONFLICT DO NOTHING",
                    (exercise_id, muscle),
                )
            inserted += 1
    conn.close()
    return inserted


def main():
    raw = extract()
    print(f"{len(raw)} exercices téléchargés depuis oss.exercisedb.dev")
    rows = transform(raw)
    count = load(rows)
    print(f"{count} exercices chargés dans la base (source='exercisedb')")


if __name__ == "__main__":
    main()

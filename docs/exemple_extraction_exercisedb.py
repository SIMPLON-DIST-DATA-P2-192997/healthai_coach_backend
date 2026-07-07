"""EXEMPLE (à adapter par l'équipe ETL) — extraction + chargement du catalogue d'exercices.

Ce script n'est PAS le livrable du Sprint 2 : l'ETL réel (etl/extract/,
etl/transform/, etl/load/) reste sous la responsabilité de l'équipe qui
travaille sur le module exercises. C'est une démonstration bout en bout,
volontairement placée dans docs/, pour :

1. Prouver que l'extraction fonctionne réellement. Source retenue :
   free-exercise-db (873 exercices, domaine public, un seul fichier JSON,
   ni pagination ni clé API) plutôt que l'API oss.exercisedb.dev, dont le
   tier gratuit plafonne à 25 exercices quel que soit le paramètre de
   pagination essayé (nextCursor, offset, page, limit élevé — tous
   ignorés en pratique). Voir database/schema/modele_donnees.md pour le
   détail de cette vérification.
2. Montrer comment peupler exercises + exercise_secondary_muscles à
   partir de champs qui se présentent comme des tableaux côté source
   mais sont en réalité mono-valués (sauf secondaryMuscles).

Usage :
    pip install psycopg2-binary
    DATABASE_URL=postgresql://user:pass@host:5432/db python docs/exemple_extraction_exercisedb.py
"""

import json
import os
import urllib.request

import psycopg2

SOURCE_URL = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json"
IMAGE_BASE_URL = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/"
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://healthai:changeme@localhost:5432/healthai_coach"
)


def extract():
    """Télécharge le dataset complet (pas de pagination, pas de clé API)."""
    req = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def transform(raw_exercises):
    """Convertit chaque exercice brut en (ligne exercises, muscles secondaires).

    primaryMuscles est toujours de longueur 1 dans les données réelles (vérifié
    sur les 873 exercices) -> on prend le premier élément sans perte d'info.
    secondaryMuscles varie réellement de 0 à 10 -> table de jointure dédiée.
    """
    rows = []
    for ex in raw_exercises:
        primary_muscles = ex.get("primaryMuscles") or []
        exercise_row = {
            "external_id": ex["id"],
            "source": "free-exercise-db",
            "name": ex["name"],
            "category": ex.get("category"),
            "equipment": ex.get("equipment"),
            "primary_muscle": primary_muscles[0] if primary_muscles else None,
            "level": ex.get("level"),
            "mechanic": ex.get("mechanic"),
            "force": ex.get("force"),
            "gif_url": (IMAGE_BASE_URL + ex["images"][0]) if ex.get("images") else None,
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
                    (external_id, source, name, category, equipment, primary_muscle,
                     level, mechanic, force, gif_url, instructions)
                VALUES (%(external_id)s, %(source)s, %(name)s, %(category)s, %(equipment)s,
                        %(primary_muscle)s, %(level)s, %(mechanic)s, %(force)s, %(gif_url)s,
                        %(instructions)s)
                ON CONFLICT (source, external_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    category = EXCLUDED.category,
                    equipment = EXCLUDED.equipment,
                    primary_muscle = EXCLUDED.primary_muscle,
                    level = EXCLUDED.level,
                    mechanic = EXCLUDED.mechanic,
                    force = EXCLUDED.force,
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
    print(f"{len(raw)} exercices téléchargés depuis free-exercise-db")
    rows = transform(raw)
    count = load(rows)
    print(f"{count} exercices chargés dans la base (source='free-exercise-db')")


if __name__ == "__main__":
    main()

"""normalize exercises secondary muscles

Revision ID: ae3640ea4852
Revises: 60a90856c89f
Create Date: 2026-07-07 11:12:22.731812

Source retenue pour l'extraction ExerciseDB : oss.exercisedb.dev (API
gratuite, 1500 exercices, pagination correcte via le paramètre `after` —
attention : `nextCursor`/`offset`/`page`/`limit` élevé sont silencieusement
ignorés par l'API, `limit` est plafonné à 25 par requête, cf. spec OpenAPI
`/swagger`).

Sur les 1500 exercices réels : bodyParts/equipments/targetMuscles sont
systématiquement des valeurs uniques (aucune violation de 1NF) — déjà
correctement modélisés en colonnes simples depuis le Sprint 1
(body_part/equipment/target_muscle). Seuls les muscles secondaires varient
réellement (0 à 10 valeurs selon l'exercice), d'où cette unique table de
jointure (cf. modele_donnees.md, section "Note de conception : pourquoi
EXERCISE_SECONDARY_MUSCLES seulement").
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'ae3640ea4852'
down_revision: Union[str, Sequence[str], None] = '60a90856c89f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE TABLE exercise_secondary_muscles (
            exercise_id     INTEGER NOT NULL,
            muscle          VARCHAR(100) NOT NULL,
            PRIMARY KEY (exercise_id, muscle),
            CONSTRAINT fk_exercise_secondary_muscles_exercise
                FOREIGN KEY (exercise_id) REFERENCES exercises(exercise_id) ON DELETE CASCADE
        )
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS exercise_secondary_muscles CASCADE")

"""normalize exercises secondary muscles

Revision ID: ae3640ea4852
Revises: 60a90856c89f
Create Date: 2026-07-07 11:12:22.731812

Motivation : l'extraction ExerciseDB a montré que la plupart des attributs
présentés comme des tableaux par l'API (category, equipment, primary_muscle,
level, mechanic, force) sont en réalité toujours des valeurs uniques dans les
données réelles (vérifié sur les 873 exercices de free-exercise-db) — seuls
les muscles secondaires varient réellement de 0 à 10 valeurs par exercice.
D'où la normalisation ciblée uniquement sur ce point (cf. modele_donnees.md,
section "Note de conception : pourquoi EXERCISE_SECONDARY_MUSCLES seulement").

Remplace aussi source/body_part/target_muscle par des colonnes reflétant le
vocabulaire réel de la source (category, primary_muscle, level, mechanic,
force), la source ExerciseDB retenue étant free-exercise-db et non
oss.exercisedb.dev (tier gratuit plafonné à 25 exercices, cf. même note).
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
    op.execute("ALTER TABLE exercises ALTER COLUMN source SET DEFAULT 'free-exercise-db'")
    op.execute("ALTER TABLE exercises DROP COLUMN IF EXISTS body_part")
    op.execute("ALTER TABLE exercises RENAME COLUMN target_muscle TO primary_muscle")
    op.execute("ALTER TABLE exercises ADD COLUMN category VARCHAR(50)")
    op.execute(
        "ALTER TABLE exercises ADD COLUMN level VARCHAR(20) "
        "CHECK (level IN ('beginner', 'intermediate', 'expert'))"
    )
    op.execute(
        "ALTER TABLE exercises ADD COLUMN mechanic VARCHAR(20) "
        "CHECK (mechanic IN ('compound', 'isolation'))"
    )
    op.execute(
        "ALTER TABLE exercises ADD COLUMN force VARCHAR(20) "
        "CHECK (force IN ('push', 'pull', 'static'))"
    )
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
    op.execute("ALTER TABLE exercises DROP COLUMN IF EXISTS force")
    op.execute("ALTER TABLE exercises DROP COLUMN IF EXISTS mechanic")
    op.execute("ALTER TABLE exercises DROP COLUMN IF EXISTS level")
    op.execute("ALTER TABLE exercises DROP COLUMN IF EXISTS category")
    op.execute("ALTER TABLE exercises RENAME COLUMN primary_muscle TO target_muscle")
    op.execute("ALTER TABLE exercises ADD COLUMN body_part VARCHAR(100)")
    op.execute("ALTER TABLE exercises ALTER COLUMN source SET DEFAULT 'exercisedb'")

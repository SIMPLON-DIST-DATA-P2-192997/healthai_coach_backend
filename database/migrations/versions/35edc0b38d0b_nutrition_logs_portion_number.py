"""nutrition logs portion number

Revision ID: 35edc0b38d0b
Revises: f573bbcd043b
Create Date: 2026-07-08 16:06:47.998195

Décision prise avec Johane/William (ETL) : food_items.calories_kcal est
exprimé pour une portion nommée (ex. "Scrambled Eggs (2 large)" = 180 kcal),
jamais pour un poids en grammes — serving_size_g n'est renseigné par aucune
des 3 sources Kaggle du projet (vérifié sur les datasets complets). Impossible
de calculer des calories consommées à partir de nutrition_logs.quantity_g
sans hypothèse non validée. On remplace donc :
- food_items.serving_size_g (toujours NULL, supprimé)
- nutrition_logs.quantity_g (grammes) -> nutrition_logs.portion_number
  (nombre de portions, décimal, ex. 1.5) : calories consommées =
  food_items.calories_kcal * nutrition_logs.portion_number.

Ajoute aussi food_items.category (nature de l'aliment, ex. "Vegetable",
"Meal/Processed") : présent dans la source (colonne "Category" du dataset
daily-food-and-nutrition-dataset, jusqu'ici non mappée), vérifié sur le
dataset complet (651 lignes, 46 catégories distinctes, 20 caractères max).
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '35edc0b38d0b'
down_revision: Union[str, Sequence[str], None] = 'f573bbcd043b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


UPGRADE_SQL = r"""
ALTER TABLE food_items DROP COLUMN serving_size_g;
ALTER TABLE food_items ADD COLUMN category VARCHAR(50);

ALTER TABLE nutrition_logs RENAME COLUMN quantity_g TO portion_number;

COMMENT ON COLUMN food_items.calories_kcal IS 'Apport calorique pour une portion de référence de cet aliment (kcal) — voir nutrition_logs.portion_number pour calculer les calories réellement consommées.';
COMMENT ON COLUMN food_items.category IS 'Nature de l''aliment déclarée par la source (ex. ''Vegetable'', ''Meal/Processed'', ''Protein/Fish'') — taxonomie libre à deux niveaux séparés par ''/'', propre à chaque source.';
COMMENT ON COLUMN nutrition_logs.portion_number IS 'Nombre de portions consommées (peut être décimal, ex. 1.5) — à multiplier par food_items.calories_kcal pour obtenir les calories réellement consommées, la portion de référence étant déjà encodée dans le nom de l''aliment (ex. ''Scrambled Eggs (2 large)'').';
"""

DOWNGRADE_SQL = r"""
ALTER TABLE nutrition_logs RENAME COLUMN portion_number TO quantity_g;

ALTER TABLE food_items DROP COLUMN category;
ALTER TABLE food_items ADD COLUMN serving_size_g NUMERIC(6,2) CHECK (serving_size_g > 0);

COMMENT ON COLUMN food_items.calories_kcal IS 'Apport calorique pour la portion de référence (kcal).';
COMMENT ON COLUMN food_items.serving_size_g IS 'Taille de la portion de référence (g), si connue dans la source.';
COMMENT ON COLUMN nutrition_logs.quantity_g IS 'Quantité consommée (g).';
"""


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(UPGRADE_SQL)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(DOWNGRADE_SQL)

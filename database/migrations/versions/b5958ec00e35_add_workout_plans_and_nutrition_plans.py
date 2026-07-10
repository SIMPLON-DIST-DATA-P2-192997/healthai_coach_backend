"""add workout plans and nutrition plans

Revision ID: b5958ec00e35
Revises: d2cc659225d9
Create Date: 2026-07-09 11:32:32.252048

Stockage pour les plans générés par le (futur) microservice IA du palier
Premium : plans d'entraînement et plans nutritionnels, sur le même modèle
d'historisation que diet_recommendations. plan_text est du texte libre en
attendant de connaître le contrat de réponse réel du microservice — cf.
modele_donnees.md, "Note de conception : microservice IA".
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b5958ec00e35'
down_revision: Union[str, Sequence[str], None] = 'd2cc659225d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


UPGRADE_SQL = """
CREATE TABLE workout_plans (
    workout_plan_id  BIGSERIAL PRIMARY KEY,
    user_id          INTEGER NOT NULL,
    goal             VARCHAR(255),
    plan_text        TEXT NOT NULL,
    generated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_workout_plans_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

COMMENT ON TABLE workout_plans IS 'Plans d''entraînement générés par le microservice IA (palier Premium), historisés (1 utilisateur -> N plans dans le temps).';
COMMENT ON COLUMN workout_plans.workout_plan_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN workout_plans.user_id IS 'Utilisateur destinataire du plan (FK users).';
COMMENT ON COLUMN workout_plans.goal IS 'Objectif exprimé par l''utilisateur ayant motivé la génération (ex. ''perte de poids'', ''prise de masse''), si fourni.';
COMMENT ON COLUMN workout_plans.plan_text IS 'Contenu du plan généré par le microservice IA — texte libre pour l''instant (cf. modele_donnees.md, à revoir une fois le contrat du microservice connu).';
COMMENT ON COLUMN workout_plans.generated_at IS 'Date de génération du plan.';

CREATE TABLE nutrition_plans (
    nutrition_plan_id  BIGSERIAL PRIMARY KEY,
    user_id            INTEGER NOT NULL,
    goal               VARCHAR(255),
    plan_text          TEXT NOT NULL,
    generated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_nutrition_plans_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

COMMENT ON TABLE nutrition_plans IS 'Plans nutritionnels générés par le microservice IA (palier Premium), historisés (1 utilisateur -> N plans dans le temps).';
COMMENT ON COLUMN nutrition_plans.nutrition_plan_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN nutrition_plans.user_id IS 'Utilisateur destinataire du plan (FK users).';
COMMENT ON COLUMN nutrition_plans.goal IS 'Objectif exprimé par l''utilisateur ayant motivé la génération (ex. ''végétarien riche en protéines''), si fourni.';
COMMENT ON COLUMN nutrition_plans.plan_text IS 'Contenu du plan généré par le microservice IA — texte libre pour l''instant (cf. modele_donnees.md, à revoir une fois le contrat du microservice connu).';
COMMENT ON COLUMN nutrition_plans.generated_at IS 'Date de génération du plan.';

CREATE INDEX idx_workout_plans_user_generated_at ON workout_plans (user_id, generated_at);
CREATE INDEX idx_nutrition_plans_user_generated_at ON nutrition_plans (user_id, generated_at);
"""

DOWNGRADE_SQL = """
DROP TABLE IF EXISTS nutrition_plans;
DROP TABLE IF EXISTS workout_plans;
"""


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(UPGRADE_SQL)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(DOWNGRADE_SQL)

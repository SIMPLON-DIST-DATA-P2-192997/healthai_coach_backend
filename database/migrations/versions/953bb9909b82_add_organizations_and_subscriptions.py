"""add organizations and subscriptions

Revision ID: 953bb9909b82
Revises: f573bbcd043b
Create Date: 2026-07-08 15:49:00.301180

Ajoute le modèle économique (cf. database/schema/modele_donnees.md, section
"Note de conception : modèle économique") : `organizations` porte les
partenaires B2B en marque blanche (salles de sport, mutuelles, entreprises),
`subscriptions` historise les souscriptions des utilisateurs (free, premium,
premium_plus, b2b) plutôt qu'un simple champ sur `users`, pour garder la
trace des changements de palier dans le temps.
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '953bb9909b82'
down_revision: Union[str, Sequence[str], None] = 'f573bbcd043b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


UPGRADE_SQL = """
CREATE TABLE organizations (
    organization_id  SERIAL PRIMARY KEY,
    name             VARCHAR(255) NOT NULL,
    contact_email    VARCHAR(255) NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE organizations IS 'Organisations partenaires (salles de sport, mutuelles, entreprises) pour l''offre B2B en marque blanche.';
COMMENT ON COLUMN organizations.organization_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN organizations.name IS 'Nom de l''organisation.';
COMMENT ON COLUMN organizations.contact_email IS 'Email de contact référent côté organisation.';
COMMENT ON COLUMN organizations.created_at IS 'Date de création de la fiche organisation.';

CREATE TABLE subscriptions (
    subscription_id  BIGSERIAL PRIMARY KEY,
    user_id          INTEGER NOT NULL,
    organization_id  INTEGER,
    tier             VARCHAR(20) NOT NULL CHECK (tier IN ('free', 'premium', 'premium_plus', 'b2b')),
    status           VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'expired')),
    price_eur_cents  INTEGER CHECK (price_eur_cents >= 0),
    started_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at         TIMESTAMPTZ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_subscriptions_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_subscriptions_organization FOREIGN KEY (organization_id) REFERENCES organizations(organization_id) ON DELETE RESTRICT,
    CONSTRAINT chk_subscriptions_ended_after_started CHECK (ended_at IS NULL OR ended_at >= started_at),
    CONSTRAINT chk_subscriptions_b2b_organization
        CHECK ((tier = 'b2b' AND organization_id IS NOT NULL) OR (tier <> 'b2b' AND organization_id IS NULL))
);

COMMENT ON TABLE subscriptions IS 'Historique des souscriptions des utilisateurs (free, premium, premium_plus, b2b) — cf. modele_donnees.md pour le modèle économique.';
COMMENT ON COLUMN subscriptions.subscription_id IS 'Identifiant technique (clé primaire).';
COMMENT ON COLUMN subscriptions.user_id IS 'Utilisateur souscripteur (FK users).';
COMMENT ON COLUMN subscriptions.organization_id IS 'Organisation de rattachement B2B (FK organizations), renseignée uniquement si tier = ''b2b'' (cf. contrainte chk_subscriptions_b2b_organization).';
COMMENT ON COLUMN subscriptions.tier IS 'Palier souscrit : free, premium, premium_plus ou b2b.';
COMMENT ON COLUMN subscriptions.status IS 'Statut de la souscription : active, cancelled ou expired.';
COMMENT ON COLUMN subscriptions.price_eur_cents IS 'Prix convenu au moment de la souscription (centimes d''euro) — valeur informative, aucune intégration de paiement dans ce lot (cf. modele_donnees.md).';
COMMENT ON COLUMN subscriptions.started_at IS 'Début de la souscription.';
COMMENT ON COLUMN subscriptions.ended_at IS 'Fin de la souscription (résiliation ou changement de palier), optionnelle si toujours active.';
COMMENT ON COLUMN subscriptions.created_at IS 'Date d''enregistrement de la ligne en base.';

CREATE INDEX idx_subscriptions_user_started_at ON subscriptions (user_id, started_at);
CREATE UNIQUE INDEX uq_subscriptions_one_active_per_user ON subscriptions (user_id) WHERE status = 'active';
"""


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(UPGRADE_SQL)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS subscriptions, organizations CASCADE")

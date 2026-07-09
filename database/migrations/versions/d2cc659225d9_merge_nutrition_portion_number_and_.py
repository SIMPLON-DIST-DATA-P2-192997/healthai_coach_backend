"""merge nutrition portion number and subscriptions

Revision ID: d2cc659225d9
Revises: 35edc0b38d0b, 953bb9909b82
Create Date: 2026-07-09 10:34:34.654279

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = 'd2cc659225d9'
down_revision: Union[str, Sequence[str], None] = ('35edc0b38d0b', '953bb9909b82')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

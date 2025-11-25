"""remove firstname, lastname default from user

Revision ID: 225fba1d7250
Revises: 7c19a72d2c80
Create Date: 2025-11-24 13:00:00.112416

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '225fba1d7250'
down_revision: Union[str, Sequence[str], None] = '7c19a72d2c80'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'users',
        'firstname',
        server_default=None
    )
    op.alter_column(
        'users',
        'lastname',
        server_default=None
    )

def downgrade() -> None:
    """Downgrade schema."""
    pass

"""category_kind

Adds a kind (expense | income) to categories so income and expense have
separate category sets. Existing rows default to expense.

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-05-31 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

category_kind = postgresql.ENUM(
    'expense', 'income', name='categorykind', create_type=False
)


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    category_kind.create(bind, checkfirst=True)
    op.add_column(
        'categories',
        sa.Column('kind', category_kind, server_default='expense', nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('categories', 'kind')
    category_kind.drop(op.get_bind(), checkfirst=True)

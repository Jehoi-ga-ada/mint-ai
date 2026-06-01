"""transaction_client_id

Adds a nullable client_id to transactions so offline clients can supply a stable
idempotency key. A unique index on (user_id, client_id) prevents a replayed
queued transaction from being inserted twice; multiple NULLs are allowed
(Postgres treats NULLs as distinct) so online-created rows are unaffected.

Revision ID: f5a6b7c8d9e0
Revises: d4e5f6a7b8c9
Create Date: 2026-06-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5a6b7c8d9e0'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'transactions',
        sa.Column('client_id', sa.String(length=64), nullable=True),
    )
    op.create_index(
        'uq_transactions_user_client',
        'transactions',
        ['user_id', 'client_id'],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('uq_transactions_user_client', table_name='transactions')
    op.drop_column('transactions', 'client_id')

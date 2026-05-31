"""portfolios_split

Introduces the Portfolio entity and moves investment_transactions off accounts
onto portfolios (money-manager Accounts vs investment Portfolios are now separate).
Existing investment_transactions rows are test-only and are cleared.

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-31 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'portfolios',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=40), nullable=False),
        sa.Column('base_currency', sa.String(length=3), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )

    # Investment data so far is test-only; clear it before repointing the FK.
    op.execute('DELETE FROM investment_transactions')

    with op.batch_alter_table('investment_transactions') as batch:
        batch.drop_constraint('investment_transactions_account_id_fkey', type_='foreignkey')
        batch.drop_column('account_id')
        batch.add_column(sa.Column('portfolio_id', sa.Uuid(), nullable=False))
        batch.create_foreign_key(
            'investment_transactions_portfolio_id_fkey',
            'portfolios',
            ['portfolio_id'],
            ['id'],
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('DELETE FROM investment_transactions')

    with op.batch_alter_table('investment_transactions') as batch:
        batch.drop_constraint('investment_transactions_portfolio_id_fkey', type_='foreignkey')
        batch.drop_column('portfolio_id')
        batch.add_column(sa.Column('account_id', sa.Uuid(), nullable=False))
        batch.create_foreign_key(
            'investment_transactions_account_id_fkey',
            'accounts',
            ['account_id'],
            ['id'],
        )

    op.drop_table('portfolios')

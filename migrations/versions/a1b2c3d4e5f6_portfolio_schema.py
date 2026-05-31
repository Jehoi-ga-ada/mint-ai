"""portfolio_schema

Adds investment/portfolio foundation: extends accounts with type/currency/institution,
and introduces assets, investment_transactions, price_snapshots, fx_rates,
and networth_snapshots tables.

Revision ID: a1b2c3d4e5f6
Revises: 542ced273b44
Create Date: 2026-05-31 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '542ced273b44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Enum types are created explicitly up front (create_type=False) so they exist
# before any ADD COLUMN / CREATE TABLE references them.
asset_class = postgresql.ENUM(
    'crypto', 'metal', 'stock', 'bond', 'forex', 'cash',
    name='assetclass', create_type=False,
)
price_source = postgresql.ENUM(
    'coingecko', 'coinmarketcap', 'metal_api', 'fx_api', 'manual',
    name='pricesource', create_type=False,
)
account_type = postgresql.ENUM(
    'cash', 'bank', 'ewallet', 'broker', 'crypto_wallet', 'metal_vault',
    name='accounttype', create_type=False,
)
inv_txn_type = postgresql.ENUM(
    'buy', 'sell', 'transfer_in', 'transfer_out', 'dividend', 'interest', 'fee',
    name='invtxntype', create_type=False,
)


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    for enum_type in (asset_class, price_source, account_type, inv_txn_type):
        enum_type.create(bind, checkfirst=True)

    op.create_table(
        'assets',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=60), nullable=False),
        sa.Column('asset_class', asset_class, nullable=False),
        sa.Column('quote_currency', sa.String(length=3), nullable=False),
        sa.Column('price_source', price_source, nullable=False),
        sa.Column('source_ref', sa.String(length=60), nullable=True),
        sa.Column('precision', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('symbol'),
    )

    op.add_column(
        'accounts',
        sa.Column('type', account_type, server_default='bank', nullable=False),
    )
    op.add_column(
        'accounts',
        sa.Column('currency', sa.String(length=3), server_default='IDR', nullable=False),
    )
    op.add_column(
        'accounts',
        sa.Column('institution', sa.String(length=60), nullable=True),
    )

    op.create_table(
        'investment_transactions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('type', inv_txn_type, nullable=False),
        sa.Column('quantity', sa.Numeric(precision=28, scale=8), nullable=False),
        sa.Column('price_per_unit', sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column('fee', sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('note', sa.String(length=120), nullable=True),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('account_id', sa.Uuid(), nullable=False),
        sa.Column('asset_id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'price_snapshots',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('price', sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('as_of', sa.DateTime(), nullable=False),
        sa.Column('asset_id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('asset_id', 'as_of', 'currency', name='uq_price_asset_asof'),
    )

    op.create_table(
        'fx_rates',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('base', sa.String(length=3), nullable=False),
        sa.Column('quote', sa.String(length=3), nullable=False),
        sa.Column('rate', sa.Numeric(precision=19, scale=8), nullable=False),
        sa.Column('as_of', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('base', 'quote', 'as_of', name='uq_fx_base_quote_asof'),
    )

    op.create_table(
        'networth_snapshots',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('total_idr', sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column('total_usd', sa.Numeric(precision=19, scale=4), nullable=False),
        sa.Column('breakdown', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'date', name='uq_networth_user_date'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('networth_snapshots')
    op.drop_table('fx_rates')
    op.drop_table('price_snapshots')
    op.drop_table('investment_transactions')

    op.drop_column('accounts', 'institution')
    op.drop_column('accounts', 'currency')
    op.drop_column('accounts', 'type')

    op.drop_table('assets')

    bind = op.get_bind()
    for enum_type in (inv_txn_type, account_type, price_source, asset_class):
        enum_type.drop(bind, checkfirst=True)

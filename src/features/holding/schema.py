from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from src.infra.models.asset import AssetClass
from src.infra.models.investment_transaction import InvTxnType


class AddInvestmentTransaction(BaseModel):
    date: datetime
    type: InvTxnType
    quantity: Decimal
    price_per_unit: Decimal
    fee: Decimal = Decimal(0)
    currency: str = "USD"
    portfolio_id: UUID
    asset_id: UUID
    note: str | None = None


class InvestmentTransactionView(BaseModel):
    id: UUID
    date: datetime
    type: InvTxnType
    quantity: Decimal
    price_per_unit: Decimal
    fee: Decimal
    currency: str
    note: str | None
    asset_id: UUID
    symbol: str
    portfolio_id: UUID


class HoldingView(BaseModel):
    asset_id: UUID
    symbol: str
    name: str
    asset_class: AssetClass
    quantity: Decimal
    avg_cost: Decimal
    cost_currency: str | None
    quote_currency: str
    current_price: Decimal | None
    price_available: bool
    display_currency: str
    market_value: Decimal | None
    cost_basis: Decimal | None
    unrealized_pl: Decimal | None
    unrealized_pl_pct: Decimal | None
    realized_pl: Decimal | None


class PricePoint(BaseModel):
    price: Decimal
    currency: str
    as_of: datetime


class HoldingDetail(HoldingView):
    price_history: list[PricePoint]

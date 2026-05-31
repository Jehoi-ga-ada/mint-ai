from datetime import date as date_type
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from src.features.holding.schema import HoldingView


class AddPortfolio(BaseModel):
    name: str
    base_currency: str = "USD"


class PortfolioHistoryPoint(BaseModel):
    date: date_type
    value: Decimal


class PortfolioSummary(BaseModel):
    total_value: Decimal
    total_cost: Decimal
    unrealized_pl: Decimal
    unrealized_pl_pct: Decimal | None
    allocation: dict[str, Decimal]  # asset_class -> market value (USD)


class PortfolioView(BaseModel):
    id: UUID
    name: str
    base_currency: str
    summary: PortfolioSummary


class PortfolioDetail(PortfolioView):
    holdings: list[HoldingView]

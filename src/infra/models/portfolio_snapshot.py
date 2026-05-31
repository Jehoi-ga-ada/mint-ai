from datetime import date as date_type
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Date, Numeric

from src.shared.base_model import Base


class PortfolioSnapshot(Base):
    """Daily snapshot of a portfolio's value/cost (USD) for the value-trend chart.

    Captured on read (one upsert per portfolio per day), since pricing is on-demand.
    """

    __tablename__ = "portfolio_snapshots"
    __table_args__ = (
        UniqueConstraint("portfolio_id", "date", name="uq_portfolio_snapshot_date"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    date: Mapped[date_type] = mapped_column(Date)
    value: Mapped[Decimal] = mapped_column(Numeric(precision=19, scale=4))
    cost: Mapped[Decimal] = mapped_column(Numeric(precision=19, scale=4))

    portfolio_id: Mapped[UUID] = mapped_column(ForeignKey("portfolios.id"))

import enum
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Numeric, String

from src.shared.base_model import Base


class InvTxnType(str, enum.Enum):
    buy = "buy"
    sell = "sell"
    transfer_in = "transfer_in"
    transfer_out = "transfer_out"
    dividend = "dividend"
    interest = "interest"
    fee = "fee"


class InvestmentTransaction(Base):
    """A single investment trade/lot. Holdings are derived from these."""

    __tablename__ = "investment_transactions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    date: Mapped[datetime] = mapped_column(default=datetime.now)
    type: Mapped[InvTxnType] = mapped_column(Enum(InvTxnType))
    quantity: Mapped[Decimal] = mapped_column(Numeric(precision=28, scale=8))
    price_per_unit: Mapped[Decimal] = mapped_column(Numeric(precision=19, scale=4))
    fee: Mapped[Decimal] = mapped_column(Numeric(precision=19, scale=4), default=0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    note: Mapped[str | None] = mapped_column(String(120))

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="investment_transactions")

    portfolio_id: Mapped[UUID] = mapped_column(ForeignKey("portfolios.id"))
    portfolio: Mapped["Portfolio"] = relationship(back_populates="investment_transactions")

    asset_id: Mapped[UUID] = mapped_column(ForeignKey("assets.id"))
    asset: Mapped["Asset"] = relationship(back_populates="investment_transactions")

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime, Numeric, String

from src.shared.base_model import Base


class FxRate(Base):
    """Exchange rate from `base` into `quote` at a point in time."""

    __tablename__ = "fx_rates"
    __table_args__ = (
        UniqueConstraint("base", "quote", "as_of", name="uq_fx_base_quote_asof"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    base: Mapped[str] = mapped_column(String(3))
    quote: Mapped[str] = mapped_column(String(3))
    rate: Mapped[Decimal] = mapped_column(Numeric(precision=19, scale=8))
    as_of: Mapped[datetime] = mapped_column(DateTime)

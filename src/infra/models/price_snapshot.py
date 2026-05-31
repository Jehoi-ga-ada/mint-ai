from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, Numeric, String

from src.shared.base_model import Base


class PriceSnapshot(Base):
    """Cached quote for an asset at a point in time (valuation + history)."""

    __tablename__ = "price_snapshots"
    __table_args__ = (
        UniqueConstraint("asset_id", "as_of", "currency", name="uq_price_asset_asof"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    price: Mapped[Decimal] = mapped_column(Numeric(precision=19, scale=4))
    currency: Mapped[str] = mapped_column(String(3))
    as_of: Mapped[datetime] = mapped_column(DateTime)

    asset_id: Mapped[UUID] = mapped_column(ForeignKey("assets.id"))
    asset: Mapped["Asset"] = relationship(back_populates="price_snapshots")

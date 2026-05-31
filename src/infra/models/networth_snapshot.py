from datetime import date as date_type
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Date, Numeric

from src.shared.base_model import Base


class NetWorthSnapshot(Base):
    """Daily rollup of a user's net worth so trend charts don't recompute history."""

    __tablename__ = "networth_snapshots"
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_networth_user_date"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    date: Mapped[date_type] = mapped_column(Date)
    total_idr: Mapped[Decimal] = mapped_column(Numeric(precision=19, scale=4))
    total_usd: Mapped[Decimal] = mapped_column(Numeric(precision=19, scale=4))
    breakdown: Mapped[dict] = mapped_column(JSONB)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="networth_snapshots")

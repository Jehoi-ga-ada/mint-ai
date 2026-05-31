from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, WriteOnlyMapped, mapped_column, relationship
from sqlalchemy.types import String

from src.shared.base_model import Base


class Portfolio(Base):
    """A named investment portfolio (e.g. 'Long-term', 'Crypto'). USD-based.

    Holds investment transactions; distinct from money-manager Accounts.
    """

    __tablename__ = "portfolios"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(40))
    base_currency: Mapped[str] = mapped_column(String(3), default="USD")

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="portfolios")

    investment_transactions: WriteOnlyMapped["InvestmentTransaction"] = relationship(
        back_populates="portfolio",
    )

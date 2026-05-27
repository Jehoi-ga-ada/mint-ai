import enum
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Numeric, String

from src.shared.base_model import Base


class TypeEnum(enum.Enum):
    income = 1
    expense = 2


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    date: Mapped[datetime] = mapped_column(default=datetime.now)
    currency: Mapped[str] = mapped_column(String(30))
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=19, scale=4))
    type: Mapped[TypeEnum] = mapped_column(Enum(TypeEnum))
    note: Mapped[str | None] = mapped_column(String(120))

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="transactions")

    category_id: Mapped[UUID] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship(back_populates="transactions")

    account_id: Mapped[UUID] = mapped_column(ForeignKey("accounts.id"))
    account: Mapped["Account"] = relationship(back_populates="transactions")

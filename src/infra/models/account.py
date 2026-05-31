import enum
from uuid import UUID, uuid4

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, WriteOnlyMapped, mapped_column, relationship
from sqlalchemy.types import String

from src.shared.base_model import Base


class AccountType(str, enum.Enum):
    cash = "cash"
    bank = "bank"
    ewallet = "ewallet"
    broker = "broker"
    crypto_wallet = "crypto_wallet"
    metal_vault = "metal_vault"


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(30))
    type: Mapped[AccountType] = mapped_column(
        Enum(AccountType),
        default=AccountType.bank,
    )
    currency: Mapped[str] = mapped_column(String(3), default="IDR")
    institution: Mapped[str | None] = mapped_column(String(60))

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="accounts")

    transactions: WriteOnlyMapped["Transaction"] = relationship(
        back_populates="account",
    )

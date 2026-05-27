from uuid import UUID, uuid4

from sqlalchemy.orm import Mapped, WriteOnlyMapped, mapped_column, relationship
from sqlalchemy.types import Boolean, String

from src.shared.base_model import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    email: Mapped[str] = mapped_column(String(30), unique=True)
    password_hash: Mapped[str] = mapped_column(String(120))
    disabled: Mapped[bool] = mapped_column(Boolean, default=False)

    transactions: WriteOnlyMapped["Transaction"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    categories: WriteOnlyMapped["Category"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    accounts: WriteOnlyMapped["Account"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

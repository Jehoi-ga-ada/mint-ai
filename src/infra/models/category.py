from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, WriteOnlyMapped, mapped_column, relationship
from sqlalchemy.types import String

from src.shared.base_model import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(30))

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="categories")

    transactions: WriteOnlyMapped["Transaction"] = relationship(
        back_populates="category",
    )

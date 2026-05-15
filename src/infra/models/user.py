from uuid import UUID, uuid4

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Boolean, String

from src.shared.base_model import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(30))
    password_hash: Mapped[str] = mapped_column(String(120))
    disabled: Mapped[bool] = mapped_column(Boolean, default=False)

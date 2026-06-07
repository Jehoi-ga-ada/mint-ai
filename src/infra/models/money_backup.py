from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Integer, Text

from src.shared.base_model import Base


class MoneyBackup(Base):
    """Snapshot backup of a user's on-device Money Manager state.

    The device is the source of truth; this is one opaque JSON blob per user,
    replaced wholesale on every upload and restored onto pristine installs.
    created_at/updated_at come from Base.
    """

    __tablename__ = "money_backups"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=True)
    data: Mapped[str] = mapped_column(Text)
    schema_version: Mapped[int] = mapped_column(Integer, default=1)

import enum
from uuid import UUID, uuid4

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, WriteOnlyMapped, mapped_column, relationship
from sqlalchemy.types import Integer, String

from src.shared.base_model import Base


class AssetClass(str, enum.Enum):
    crypto = "crypto"
    metal = "metal"
    stock = "stock"
    bond = "bond"
    forex = "forex"
    cash = "cash"


class PriceSource(str, enum.Enum):
    coingecko = "coingecko"
    coinmarketcap = "coinmarketcap"
    metal_api = "metal_api"
    fx_api = "fx_api"
    manual = "manual"


class Asset(Base):
    """Instrument reference catalog (seeded; shared across users)."""

    __tablename__ = "assets"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    symbol: Mapped[str] = mapped_column(String(20), unique=True)
    name: Mapped[str] = mapped_column(String(60))
    asset_class: Mapped[AssetClass] = mapped_column(Enum(AssetClass))
    quote_currency: Mapped[str] = mapped_column(String(3), default="USD")
    price_source: Mapped[PriceSource] = mapped_column(
        Enum(PriceSource),
        default=PriceSource.manual,
    )
    source_ref: Mapped[str | None] = mapped_column(String(60))
    precision: Mapped[int] = mapped_column(Integer, default=8)

    investment_transactions: WriteOnlyMapped["InvestmentTransaction"] = relationship(
        back_populates="asset",
    )
    price_snapshots: WriteOnlyMapped["PriceSnapshot"] = relationship(
        back_populates="asset",
    )

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class AssetPrice(BaseModel):
    asset_id: str
    symbol: str
    price: Decimal | None
    currency: str
    available: bool
    as_of: datetime | None = None


class CreateAsset(BaseModel):
    """User-added token. Symbol is enough — price providers (CoinMarketCap,
    keyless Coinbase fallback) quote crypto by ticker."""

    symbol: str = Field(min_length=1, max_length=20, pattern=r"^[A-Za-z0-9]+$")
    name: str | None = Field(default=None, max_length=60)

    @field_validator("symbol")
    @classmethod
    def uppercase(cls, value: str) -> str:
        return value.upper()

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class AssetPrice(BaseModel):
    asset_id: str
    symbol: str
    price: Decimal | None
    currency: str
    available: bool
    as_of: datetime | None = None

from typing import Sequence
from uuid import UUID

from src.features.asset.starters import STARTER_ASSETS
from src.infra.models.asset import Asset, AssetClass, PriceSource
from src.infra.repos.asset_repo import AssetRepo


class AssetService:
    def __init__(self, repo: AssetRepo) -> None:
        self.repo = repo

    def seed_catalog(self) -> int:
        """Insert any missing starter assets. Idempotent. Returns count created."""
        created = 0
        for entry in STARTER_ASSETS:
            if self.repo.exists(symbol=entry["symbol"]):
                continue
            self.repo.create(Asset(**entry))
            created += 1
        return created

    def list_assets(self) -> Sequence[Asset]:
        return self.repo.list(order_by=Asset.symbol)

    def create_token(self, symbol: str, name: str | None) -> Asset:
        """Add a user-supplied crypto token. Idempotent on symbol — adding an
        existing ticker returns the catalog entry instead of erroring."""
        existing = self.repo.get_by(symbol=symbol)
        if existing is not None:
            return existing
        return self.repo.create(
            Asset(
                symbol=symbol,
                name=name or symbol,
                asset_class=AssetClass.crypto,
                quote_currency="USD",
                price_source=PriceSource.coinmarketcap,
                source_ref=None,
                precision=8,
            )
        )

    def get(self, asset_id: UUID) -> Asset | None:
        return self.repo.get(asset_id)

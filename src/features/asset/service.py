from typing import Sequence
from uuid import UUID

from src.features.asset.starters import STARTER_ASSETS
from src.infra.models.asset import Asset
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

    def get(self, asset_id: UUID) -> Asset | None:
        return self.repo.get(asset_id)

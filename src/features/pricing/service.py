"""On-demand price & FX valuation with TTL-cached snapshots.

Prices are fetched lazily when needed; a snapshot fresher than ``ttl_seconds``
is reused. On provider failure we fall back to the most recent cached value.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.features.pricing.providers import FxProvider, PriceProvider
from src.infra.models.asset import Asset, AssetClass, PriceSource
from src.infra.models.fx_rate import FxRate
from src.infra.models.price_snapshot import PriceSnapshot
from src.infra.repos.fx_rate_repo import FxRateRepo
from src.infra.repos.price_snapshot_repo import PriceSnapshotRepo


class PriceService:
    # Asset classes the keyless fallback (Coinbase by ticker) can price.
    _FALLBACK_CLASSES = (AssetClass.crypto, AssetClass.metal)

    def __init__(
        self,
        snapshot_repo: PriceSnapshotRepo,
        providers: dict[PriceSource, PriceProvider],
        ttl_seconds: int,
        fallback: PriceProvider | None = None,
    ) -> None:
        self.snapshot_repo = snapshot_repo
        self.providers = providers
        self.ttl_seconds = ttl_seconds
        self.fallback = fallback

    def get_price(self, asset: Asset) -> Decimal | None:
        """Latest price of ``asset`` in its quote currency, or None if unavailable."""
        latest = self._latest_snapshot(asset.id, asset.quote_currency)
        if latest is not None and self._is_fresh(latest.as_of):
            return latest.price

        provider = self.providers.get(asset.price_source)
        price = provider.fetch_price(asset) if provider else None
        # Keyless fallback so prices work without a configured provider key.
        if price is None and self.fallback is not None and asset.asset_class in self._FALLBACK_CLASSES:
            price = self.fallback.fetch_price(asset)
        if price is not None:
            self.snapshot_repo.create(
                PriceSnapshot(
                    asset_id=asset.id,
                    price=price,
                    currency=asset.quote_currency,
                    as_of=datetime.now(),
                )
            )
            return price

        return latest.price if latest is not None else None

    def history(self, asset: Asset, limit: int = 90) -> list[PriceSnapshot]:
        """Most-recent price snapshots for an asset in its quote currency."""
        rows = self.snapshot_repo.list(
            limit=limit,
            order_by=PriceSnapshot.as_of.desc(),
            asset_id=asset.id,
            currency=asset.quote_currency,
        )
        return list(rows)

    def _latest_snapshot(self, asset_id: UUID, currency: str) -> PriceSnapshot | None:
        rows = self.snapshot_repo.list(
            limit=1,
            order_by=PriceSnapshot.as_of.desc(),
            asset_id=asset_id,
            currency=currency,
        )
        return rows[0] if rows else None

    def _is_fresh(self, as_of: datetime) -> bool:
        return (datetime.now() - as_of).total_seconds() < self.ttl_seconds


class FxService:
    def __init__(
        self,
        rate_repo: FxRateRepo,
        provider: FxProvider,
        ttl_seconds: int,
    ) -> None:
        self.rate_repo = rate_repo
        self.provider = provider
        self.ttl_seconds = ttl_seconds

    def get_rate(self, base: str, quote: str) -> Decimal | None:
        """Conversion rate from ``base`` into ``quote`` (1 if identical)."""
        if base == quote:
            return Decimal(1)

        latest = self._latest_rate(base, quote)
        if latest is not None and self._is_fresh(latest.as_of):
            return latest.rate

        rates = self.provider.fetch_rates(base)
        rate = rates.get(quote)
        if rate is not None:
            self.rate_repo.create(
                FxRate(base=base, quote=quote, rate=rate, as_of=datetime.now())
            )
            return rate

        return latest.rate if latest is not None else None

    def convert(self, amount: Decimal, frm: str, to: str) -> Decimal | None:
        rate = self.get_rate(frm, to)
        return amount * rate if rate is not None else None

    def _latest_rate(self, base: str, quote: str) -> FxRate | None:
        rows = self.rate_repo.list(
            limit=1,
            order_by=FxRate.as_of.desc(),
            base=base,
            quote=quote,
        )
        return rows[0] if rows else None

    def _is_fresh(self, as_of: datetime) -> bool:
        return (datetime.now() - as_of).total_seconds() < self.ttl_seconds

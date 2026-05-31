from fastapi import Depends
from sqlalchemy.orm import Session

from src.features.pricing.providers import (
    CoinbaseProvider,
    CoinGeckoProvider,
    CoinMarketCapProvider,
    FxProvider,
    MetalProvider,
)
from src.features.pricing.service import FxService, PriceService
from src.infra.config import config
from src.infra.deps import get_session
from src.infra.models.asset import PriceSource
from src.infra.repos.fx_rate_repo import FxRateRepo
from src.infra.repos.price_snapshot_repo import PriceSnapshotRepo


def get_price_service(session: Session = Depends(get_session)) -> PriceService:
    providers = {
        PriceSource.coinmarketcap: CoinMarketCapProvider(
            api_key=config.coinmarketcap_api_key
        ),
        PriceSource.coingecko: CoinGeckoProvider(api_key=config.coingecko_api_key),
        PriceSource.metal_api: MetalProvider(api_key=config.metal_api_key),
    }
    return PriceService(
        snapshot_repo=PriceSnapshotRepo(session=session),
        providers=providers,
        ttl_seconds=config.price_ttl_seconds,
        fallback=CoinbaseProvider(),
    )


def get_fx_service(session: Session = Depends(get_session)) -> FxService:
    return FxService(
        rate_repo=FxRateRepo(session=session),
        provider=FxProvider(api_key=config.fx_api_key),
        ttl_seconds=config.price_ttl_seconds,
    )

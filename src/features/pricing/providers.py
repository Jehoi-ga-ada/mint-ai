"""External price-data providers.

Each provider performs a best-effort HTTP fetch and returns ``None`` on any
failure so the caller can fall back to a cached snapshot. Providers never raise
into the request path.
"""

import logging
from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation

import httpx

from src.infra.models.asset import Asset

logger = logging.getLogger(__name__)

_TIMEOUT = httpx.Timeout(10.0)

# metals.dev returns prices keyed by metal name; map our source_ref/symbol to it.
_METAL_KEYS = {"XAU": "gold", "XAG": "silver", "XPT": "platinum", "XPD": "palladium"}


def _to_decimal(value) -> Decimal | None:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


class PriceProvider(ABC):
    """Fetches the current price of an asset in the asset's quote currency."""

    @abstractmethod
    def fetch_price(self, asset: Asset) -> Decimal | None: ...


class CoinGeckoProvider(PriceProvider):
    BASE_URL = "https://api.coingecko.com/api/v3/simple/price"

    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key

    def fetch_price(self, asset: Asset) -> Decimal | None:
        coin_id = asset.source_ref
        if not coin_id:
            return None
        vs = asset.quote_currency.lower()
        headers = {"x-cg-demo-api-key": self.api_key} if self.api_key else {}
        try:
            resp = httpx.get(
                self.BASE_URL,
                params={"ids": coin_id, "vs_currencies": vs},
                headers=headers,
                timeout=_TIMEOUT,
            )
            resp.raise_for_status()
            return _to_decimal(resp.json().get(coin_id, {}).get(vs))
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("CoinGecko fetch failed for %s: %s", asset.symbol, exc)
            return None


class CoinbaseProvider(PriceProvider):
    """Keyless spot prices by ticker (works without any API key).

    Covers crypto and tokenized metals (e.g. PAXG-USD). Used as a fallback so
    valuations work out of the box even when no paid provider key is set.
    """

    BASE_URL = "https://api.coinbase.com/v2/prices"

    def fetch_price(self, asset: Asset) -> Decimal | None:
        symbol = (asset.source_ref or asset.symbol).upper()
        pair = f"{symbol}-{asset.quote_currency.upper()}"
        try:
            resp = httpx.get(f"{self.BASE_URL}/{pair}/spot", timeout=_TIMEOUT)
            resp.raise_for_status()
            return _to_decimal(resp.json().get("data", {}).get("amount"))
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            logger.warning("Coinbase fetch failed for %s: %s", asset.symbol, exc)
            return None


class CoinMarketCapProvider(PriceProvider):
    """CoinMarketCap quotes (free 'Basic' plan; API key required)."""

    BASE_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key

    def fetch_price(self, asset: Asset) -> Decimal | None:
        symbol = (asset.source_ref or asset.symbol).upper()
        convert = asset.quote_currency.upper()
        if not symbol or not self.api_key:
            return None
        try:
            resp = httpx.get(
                self.BASE_URL,
                params={"symbol": symbol, "convert": convert},
                headers={"X-CMC_PRO_API_KEY": self.api_key},
                timeout=_TIMEOUT,
            )
            resp.raise_for_status()
            entry = resp.json().get("data", {}).get(symbol)
            # CMC may return a list per symbol on some plans; take the first.
            if isinstance(entry, list):
                entry = entry[0] if entry else None
            if not entry:
                return None
            return _to_decimal(entry.get("quote", {}).get(convert, {}).get("price"))
        except (httpx.HTTPError, ValueError, KeyError, IndexError) as exc:
            logger.warning("CoinMarketCap fetch failed for %s: %s", asset.symbol, exc)
            return None


class MetalProvider(PriceProvider):
    """metals.dev latest spot prices (per troy ounce)."""

    BASE_URL = "https://api.metals.dev/v1/latest"

    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key

    def fetch_price(self, asset: Asset) -> Decimal | None:
        metal_key = _METAL_KEYS.get((asset.source_ref or asset.symbol).upper())
        if not metal_key or not self.api_key:
            return None
        try:
            resp = httpx.get(
                self.BASE_URL,
                params={
                    "api_key": self.api_key,
                    "currency": asset.quote_currency,
                    "unit": "toz",
                },
                timeout=_TIMEOUT,
            )
            resp.raise_for_status()
            return _to_decimal(resp.json().get("metals", {}).get(metal_key))
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("Metal fetch failed for %s: %s", asset.symbol, exc)
            return None


class FxProvider:
    """Currency rates. Uses the keyless open.er-api.com by default."""

    BASE_URL = "https://open.er-api.com/v6/latest"

    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key

    def fetch_rates(self, base: str) -> dict[str, Decimal]:
        """Return a mapping of quote-currency -> rate for ``base``. Empty on failure."""
        try:
            resp = httpx.get(f"{self.BASE_URL}/{base.upper()}", timeout=_TIMEOUT)
            resp.raise_for_status()
            rates = resp.json().get("rates", {})
            return {
                ccy: rate
                for ccy, raw in rates.items()
                if (rate := _to_decimal(raw)) is not None
            }
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("FX fetch failed for base %s: %s", base, exc)
            return {}

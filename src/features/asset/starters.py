"""Seed asset catalog shared across users.

Each entry: (symbol, name, asset_class, quote_currency, price_source, source_ref, precision).
Crypto uses CoinGecko ids; metals use metals.dev metal names.
"""

from src.infra.models.asset import AssetClass, PriceSource

STARTER_ASSETS: list[dict] = [
    {
        "symbol": "BTC",
        "name": "Bitcoin",
        "asset_class": AssetClass.crypto,
        "quote_currency": "USD",
        "price_source": PriceSource.coinmarketcap,
        "source_ref": "BTC",
        "precision": 8,
    },
    {
        "symbol": "ETH",
        "name": "Ethereum",
        "asset_class": AssetClass.crypto,
        "quote_currency": "USD",
        "price_source": PriceSource.coinmarketcap,
        "source_ref": "ETH",
        "precision": 8,
    },
    {
        "symbol": "SOL",
        "name": "Solana",
        "asset_class": AssetClass.crypto,
        "quote_currency": "USD",
        "price_source": PriceSource.coinmarketcap,
        "source_ref": "SOL",
        "precision": 8,
    },
    {
        "symbol": "USDT",
        "name": "Tether",
        "asset_class": AssetClass.crypto,
        "quote_currency": "USD",
        "price_source": PriceSource.coinmarketcap,
        "source_ref": "USDT",
        "precision": 6,
    },
    {
        # Gold spot proxied via PAXG (tokenized gold ~= 1 troy oz) on CoinMarketCap.
        "symbol": "XAU",
        "name": "Gold (troy oz, via PAXG)",
        "asset_class": AssetClass.metal,
        "quote_currency": "USD",
        "price_source": PriceSource.coinmarketcap,
        "source_ref": "PAXG",
        "precision": 4,
    },
    {
        # Silver spot proxied via KAG (Kinesis Silver ~= 1 troy oz) on CoinMarketCap.
        "symbol": "XAG",
        "name": "Silver (troy oz, via KAG)",
        "asset_class": AssetClass.metal,
        "quote_currency": "USD",
        "price_source": PriceSource.coinmarketcap,
        "source_ref": "KAG",
        "precision": 4,
    },
    {
        "symbol": "USD",
        "name": "US Dollar",
        "asset_class": AssetClass.cash,
        "quote_currency": "USD",
        "price_source": PriceSource.manual,
        "source_ref": None,
        "precision": 2,
    },
    {
        "symbol": "IDR",
        "name": "Indonesian Rupiah",
        "asset_class": AssetClass.cash,
        "quote_currency": "IDR",
        "price_source": PriceSource.manual,
        "source_ref": None,
        "precision": 2,
    },
]

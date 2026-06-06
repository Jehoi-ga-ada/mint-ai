"""User-scoped portfolio tools. The chat endpoint passes the authenticated
user's id through the graph config, so the model can only ever read the data
of the user who is talking to it."""

import json
from uuid import UUID

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from src.features.holding.service import HoldingService
from src.features.portfolio.service import PortfolioService
from src.features.pricing.deps import get_price_service
from src.infra.config import config as app_config
from src.infra.database import PostgreDatabase
from src.infra.repos.asset_repo import AssetRepo
from src.infra.repos.investment_transaction_repo import InvestmentTransactionRepo
from src.infra.repos.portfolio_repo import PortfolioRepo
from src.infra.repos.portfolio_snapshot_repo import PortfolioSnapshotRepo

_db: PostgreDatabase | None = None


def _session():
    """Tools run outside FastAPI's DI, so they own a small engine of their own."""
    global _db
    if _db is None:
        _db = PostgreDatabase(app_config.db_url)
    return _db._session_factory()


def _portfolio_service(session) -> PortfolioService:
    # Mirrors the FastAPI deps wiring (deps.py) for use outside a request —
    # the deps builders are plain functions, so they compose directly.
    price_service = get_price_service(session)
    holding_service = HoldingService(
        txn_repo=InvestmentTransactionRepo(session=session),
        asset_repo=AssetRepo(session=session),
        portfolio_repo=PortfolioRepo(session=session),
        price_service=price_service,
    )
    return PortfolioService(
        repo=PortfolioRepo(session=session),
        holding_service=holding_service,
        snapshot_repo=PortfolioSnapshotRepo(session=session),
    )


def _user_id(config: RunnableConfig) -> UUID | None:
    raw = (config.get("configurable") or {}).get("user_id")
    try:
        return UUID(raw) if raw else None
    except ValueError:
        return None


@tool
def get_my_portfolios(config: RunnableConfig) -> str:
    """Get the signed-in user's investment portfolios with their holdings:
    quantities, live USD prices, market values, cost basis, and unrealized P/L.
    Use this whenever the user asks about their portfolio, holdings,
    investments, allocation, or performance."""
    user_id = _user_id(config)
    if user_id is None:
        return "No signed-in user context available."
    session = _session()
    try:
        service = _portfolio_service(session)
        payload = []
        for view in service.list_with_summary(user_id):
            detail = service.get_detail(view.id, user_id)
            payload.append(
                {
                    "name": view.name,
                    "currency": view.base_currency,
                    "total_value": view.summary.total_value,
                    "total_cost": view.summary.total_cost,
                    "unrealized_pl": view.summary.unrealized_pl,
                    "unrealized_pl_pct": view.summary.unrealized_pl_pct,
                    "holdings": [
                        {
                            "symbol": h.symbol,
                            "name": h.name,
                            "asset_class": h.asset_class,
                            "quantity": h.quantity,
                            "avg_cost": h.avg_cost,
                            "current_price": h.current_price,
                            "market_value": h.market_value,
                            "unrealized_pl": h.unrealized_pl,
                        }
                        for h in (detail.holdings if detail else [])
                    ],
                }
            )
        session.commit()  # valuation captures daily snapshots
        return json.dumps({"portfolios": payload}, default=str)
    finally:
        session.close()


MAX_TXNS = 50


@tool
def get_my_investment_transactions(config: RunnableConfig) -> str:
    """Get the signed-in user's recent investment transactions (buys/sells)
    across all their portfolios: asset, quantity, price, total, and date. Use
    this when the user asks what they bought or sold, their cost basis
    history, or trading activity."""
    user_id = _user_id(config)
    if user_id is None:
        return "No signed-in user context available."
    session = _session()
    try:
        service = _portfolio_service(session)
        rows = []
        for view in service.list_with_summary(user_id):
            for t in service.list_transactions(view.id, user_id) or []:
                rows.append(
                    {
                        "portfolio": view.name,
                        "date": t.date,
                        "type": t.type,
                        "symbol": t.symbol,
                        "quantity": t.quantity,
                        "price_per_unit": t.price_per_unit,
                        "fee": t.fee,
                        "currency": t.currency,
                        "note": t.note,
                    }
                )
        rows.sort(key=lambda r: str(r["date"]), reverse=True)
        session.commit()
        return json.dumps({"transactions": rows[:MAX_TXNS]}, default=str)
    finally:
        session.close()

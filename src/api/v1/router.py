from fastapi import APIRouter

from src.api.v1.endpoints.account import router as account_router
from src.api.v1.endpoints.asset import router as asset_router
from src.api.v1.endpoints.auth import router as auth_router
from src.api.v1.endpoints.category import router as category_router
from src.api.v1.endpoints.chat import router as chat_router
from src.api.v1.endpoints.health import router as health_router
from src.api.v1.endpoints.investment import router as investment_router
from src.api.v1.endpoints.money import router as money_router
from src.api.v1.endpoints.portfolio import router as portfolio_router
from src.api.v1.endpoints.ready import router as ready_router
from src.api.v1.endpoints.transaction import router as transaction_router

router = APIRouter(prefix="/api/v1")
endpoints = [
    health_router,
    ready_router,
    auth_router,
    chat_router,
    # Money manager (daily income/expense, IDR)
    account_router,
    category_router,
    transaction_router,
    money_router,
    # Investment portfolio (USD)
    portfolio_router,
    asset_router,
    investment_router,
]

for e in endpoints:
    router.include_router(e)

from fastapi import APIRouter

from src.api.v1.endpoints.auth import router as auth_router
from src.api.v1.endpoints.chat import router as chat_router
from src.api.v1.endpoints.health import router as health_router
from src.api.v1.endpoints.ready import router as ready_router

router = APIRouter(prefix="/api/v1")
endpoints = [health_router, ready_router, auth_router, chat_router]

for e in endpoints:
    router.include_router(e)

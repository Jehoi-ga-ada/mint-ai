from fastapi import APIRouter

from src.api.v1.endpoints.health import router as health_router

router = APIRouter(prefix="/api/v1")
endpoints = [health_router]

for e in endpoints:
    router.include_router(e)

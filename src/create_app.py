from fastapi import FastAPI

from src.api.legal import router as legal_router
from src.api.v1.router import router
from src.infra.container import setup_container


def create_app():
    app = FastAPI()

    setup_container(app)

    app.include_router(router)
    app.include_router(legal_router)

    return app

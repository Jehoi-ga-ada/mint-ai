from fastapi import FastAPI

from src.api.v1.router import router
from src.infra.container import setup_container


def create_app():
    app = FastAPI()

    setup_container(app)

    app.include_router(router)

    return app

from fastapi import FastAPI

from src.infra.container import setup_container


def create_app():
    app = FastAPI()

    setup_container(app)

    return app

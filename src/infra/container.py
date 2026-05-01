from dependency_injector import containers, providers

from src.infra.config import config
from src.infra.database import PostgreDatabase


def setup_container(app):
    app.container = Container()


class Container(containers.DeclarativeContainer):
    db = providers.Singleton(PostgreDatabase, config.db_url)

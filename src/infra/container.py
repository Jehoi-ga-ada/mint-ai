from dependency_injector import containers, providers

from src import api
from src.infra.config import config
from src.infra.database import PostgreDatabase


def setup_container(app):
    app.container = Container()


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=[api])

    db = providers.Singleton(PostgreDatabase, db_url=config.db_url)

from dependency_injector import containers, providers

from src import api
from src.features.readiness import CheckReadyService
from src.infra.config import config
from src.infra.database import PostgreDatabase


def setup_container(app):
    app.container = Container()


def session_resource(db: PostgreDatabase):
    session = db.get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=[api])

    db = providers.Singleton(PostgreDatabase, db_url=config.db_url)

    session = providers.Resource(session_resource, db=db)

    check_ready_service = providers.Factory(CheckReadyService, session=session)

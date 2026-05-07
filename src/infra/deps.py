from fastapi import Depends, Request

from src.infra.database import PostgreDatabase


def get_db(request: Request) -> PostgreDatabase:
    return request.app.container.db()


def get_session(db: PostgreDatabase = Depends(get_db)):
    session = db.get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

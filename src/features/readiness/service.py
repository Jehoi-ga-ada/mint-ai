from sqlalchemy import text
from sqlalchemy.orm import Session

from src.features.readiness.schema import Ready


class CheckReadyService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def ping_db(self) -> bool:
        try:
            self.session.execute(text("SELECT 1"))
            return True
        except Exception as _:
            return False

    def ready(self) -> Ready:
        postgres_ready = self.ping_db()
        response = Ready()

        if postgres_ready:
            response.postgres = "ready"
        else:
            response.postgres = "not ready"

        return response

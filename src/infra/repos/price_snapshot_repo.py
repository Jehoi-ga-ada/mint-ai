from sqlalchemy.orm import Session

from src.infra.models.price_snapshot import PriceSnapshot
from src.shared.base_repo import BaseRepo


class PriceSnapshotRepo(BaseRepo[PriceSnapshot]):
    model = PriceSnapshot

    def __init__(self, session: Session) -> None:
        super().__init__(session)

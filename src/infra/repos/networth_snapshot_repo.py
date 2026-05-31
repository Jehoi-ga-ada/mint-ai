from sqlalchemy.orm import Session

from src.infra.models.networth_snapshot import NetWorthSnapshot
from src.shared.base_repo import BaseRepo


class NetWorthSnapshotRepo(BaseRepo[NetWorthSnapshot]):
    model = NetWorthSnapshot

    def __init__(self, session: Session) -> None:
        super().__init__(session)

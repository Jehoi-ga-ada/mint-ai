from sqlalchemy.orm import Session

from src.infra.models.portfolio_snapshot import PortfolioSnapshot
from src.shared.base_repo import BaseRepo


class PortfolioSnapshotRepo(BaseRepo[PortfolioSnapshot]):
    model = PortfolioSnapshot

    def __init__(self, session: Session) -> None:
        super().__init__(session)

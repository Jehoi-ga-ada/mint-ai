from sqlalchemy.orm import Session

from src.infra.models.portfolio import Portfolio
from src.shared.base_repo import BaseRepo


class PortfolioRepo(BaseRepo[Portfolio]):
    model = Portfolio

    def __init__(self, session: Session) -> None:
        super().__init__(session)

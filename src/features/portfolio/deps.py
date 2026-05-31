from fastapi import Depends
from sqlalchemy.orm import Session

from src.features.holding.deps import get_holding_service
from src.features.holding.service import HoldingService
from src.features.portfolio.service import PortfolioService
from src.infra.deps import get_session
from src.infra.repos.portfolio_repo import PortfolioRepo
from src.infra.repos.portfolio_snapshot_repo import PortfolioSnapshotRepo


def get_portfolio_repo(session: Session = Depends(get_session)):
    return PortfolioRepo(session=session)


def get_portfolio_service(
    repo: PortfolioRepo = Depends(get_portfolio_repo),
    holding_service: HoldingService = Depends(get_holding_service),
    session: Session = Depends(get_session),
) -> PortfolioService:
    return PortfolioService(
        repo=repo,
        holding_service=holding_service,
        snapshot_repo=PortfolioSnapshotRepo(session=session),
    )

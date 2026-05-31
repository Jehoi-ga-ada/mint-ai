from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.features.auth.deps import get_current_user
from src.features.portfolio.deps import get_portfolio_service
from src.features.portfolio.schema import AddPortfolio
from src.features.portfolio.service import PortfolioService
from src.infra.models.user import User

router = APIRouter(prefix="/portfolios")


@router.get("")
def list_portfolios(
    service: PortfolioService = Depends(get_portfolio_service),
    user: User = Depends(get_current_user),
):
    return service.list_with_summary(user_id=user.id)


@router.post("")
def create_portfolio(
    payload: AddPortfolio,
    service: PortfolioService = Depends(get_portfolio_service),
    user: User = Depends(get_current_user),
):
    return service.create(payload=payload, user_id=user.id)


@router.get("/{portfolio_id}")
def get_portfolio(
    portfolio_id: UUID,
    service: PortfolioService = Depends(get_portfolio_service),
    user: User = Depends(get_current_user),
):
    detail = service.get_detail(portfolio_id=portfolio_id, user_id=user.id)
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="portfolio_not_found"
        )
    return detail


@router.get("/{portfolio_id}/history")
def get_portfolio_history(
    portfolio_id: UUID,
    start: date | None = None,
    end: date | None = None,
    service: PortfolioService = Depends(get_portfolio_service),
    user: User = Depends(get_current_user),
):
    history = service.get_history(
        portfolio_id=portfolio_id, user_id=user.id, start=start, end=end
    )
    if history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="portfolio_not_found"
        )
    return history


@router.get("/{portfolio_id}/transactions")
def get_portfolio_transactions(
    portfolio_id: UUID,
    service: PortfolioService = Depends(get_portfolio_service),
    user: User = Depends(get_current_user),
):
    txns = service.list_transactions(portfolio_id=portfolio_id, user_id=user.id)
    if txns is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="portfolio_not_found"
        )
    return txns

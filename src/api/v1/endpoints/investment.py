from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.features.auth.deps import get_current_user
from src.features.holding.deps import get_holding_service
from src.features.holding.schema import AddInvestmentTransaction
from src.features.holding.service import HoldingService
from src.infra.models.user import User

router = APIRouter(prefix="/investment")


@router.post("/transaction")
def create_investment_transaction(
    payload: AddInvestmentTransaction,
    service: HoldingService = Depends(get_holding_service),
    user: User = Depends(get_current_user),
):
    try:
        return service.add_transaction(payload=payload, user_id=user.id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="portfolio_not_found"
        )


@router.put("/transaction/{transaction_id}")
def update_investment_transaction(
    transaction_id: UUID,
    payload: AddInvestmentTransaction,
    service: HoldingService = Depends(get_holding_service),
    user: User = Depends(get_current_user),
):
    try:
        return service.update_transaction(transaction_id, payload, user.id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="transaction_not_found"
        )


@router.delete("/transaction/{transaction_id}")
def delete_investment_transaction(
    transaction_id: UUID,
    service: HoldingService = Depends(get_holding_service),
    user: User = Depends(get_current_user),
):
    try:
        service.delete_transaction(transaction_id, user.id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="transaction_not_found"
        )
    return {"status": "deleted"}

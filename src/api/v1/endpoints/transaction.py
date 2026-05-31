from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.features.auth.deps import get_current_user
from src.features.transaction.deps import get_transaction_service
from src.features.transaction.schema import AddTransaction
from src.features.transaction.service import TransactionService
from src.infra.models.user import User

router = APIRouter(prefix="/transaction")


@router.post("/create")
def create_transaction(
    payload: AddTransaction,
    service: TransactionService = Depends(get_transaction_service),
    user: User = Depends(get_current_user),
):
    return service.add_transaction(payload=payload, user_id=user.id)


@router.put("/{transaction_id}")
def update_transaction(
    transaction_id: UUID,
    payload: AddTransaction,
    service: TransactionService = Depends(get_transaction_service),
    user: User = Depends(get_current_user),
):
    try:
        return service.update_transaction(transaction_id, payload, user.id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="transaction_not_found"
        )


@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: UUID,
    service: TransactionService = Depends(get_transaction_service),
    user: User = Depends(get_current_user),
):
    try:
        service.delete_transaction(transaction_id, user.id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="transaction_not_found"
        )
    return {"status": "deleted"}

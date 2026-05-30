from fastapi import APIRouter, Depends

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

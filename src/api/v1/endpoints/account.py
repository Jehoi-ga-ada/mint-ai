from fastapi import APIRouter, Depends

from src.features.account.deps import get_account_service
from src.features.account.schema import AddAccount
from src.features.account.service import AccountService
from src.features.auth.deps import get_current_user
from src.infra.models.user import User

router = APIRouter(prefix="/accounts")


@router.get("")
def list_accounts(
    service: AccountService = Depends(get_account_service),
    user: User = Depends(get_current_user),
):
    return service.list_accounts(user_id=user.id)


@router.post("")
def create_account(
    payload: AddAccount,
    service: AccountService = Depends(get_account_service),
    user: User = Depends(get_current_user),
):
    return service.create_account(payload=payload, user_id=user.id)

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.features.auth.deps import get_current_user
from src.features.money.deps import get_money_service
from src.features.money.service import MoneyService
from src.infra.models.transaction import TypeEnum
from src.infra.models.user import User

router = APIRouter(prefix="/money")


@router.get("/transactions")
def list_transactions(
    type: TypeEnum | None = None,
    account_id: UUID | None = None,
    start: date | None = None,
    end: date | None = None,
    limit: int = Query(200, ge=1, le=1000),
    service: MoneyService = Depends(get_money_service),
    user: User = Depends(get_current_user),
):
    return service.list_transactions(
        user_id=user.id,
        txn_type=type,
        account_id=account_id,
        start=start,
        end=end,
        limit=limit,
    )


@router.get("/summary")
def money_summary(
    service: MoneyService = Depends(get_money_service),
    user: User = Depends(get_current_user),
):
    return service.summary(user_id=user.id)


@router.get("/stats")
def money_stats(
    type: TypeEnum = TypeEnum.expense,
    start: date | None = None,
    end: date | None = None,
    service: MoneyService = Depends(get_money_service),
    user: User = Depends(get_current_user),
):
    return service.stats(user_id=user.id, txn_type=type, start=start, end=end)

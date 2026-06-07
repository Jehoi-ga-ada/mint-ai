from datetime import date, datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.features.auth.deps import get_current_user
from src.features.money.backup import MoneyBackupService
from src.features.money.deps import get_money_backup_service, get_money_service
from src.features.money.schema import MoneyBackupIn, MoneyBackupOut
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


@router.get("/backup")
def get_money_backup(
    service: MoneyBackupService = Depends(get_money_backup_service),
    user: User = Depends(get_current_user),
) -> MoneyBackupOut:
    backup = service.get(user_id=user.id)
    if backup is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no_backup")
    return MoneyBackupOut(
        data=backup.data,
        schema_version=backup.schema_version,
        updated_at=backup.updated_at,
    )


@router.put("/backup")
def put_money_backup(
    payload: MoneyBackupIn,
    service: MoneyBackupService = Depends(get_money_backup_service),
    user: User = Depends(get_current_user),
) -> MoneyBackupOut:
    backup = service.put(
        user_id=user.id, data=payload.data, schema_version=payload.schema_version
    )
    return MoneyBackupOut(
        data=backup.data,
        schema_version=backup.schema_version,
        updated_at=backup.updated_at or datetime.now(timezone.utc),
    )

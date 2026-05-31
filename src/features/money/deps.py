from fastapi import Depends
from sqlalchemy.orm import Session

from src.features.money.service import MoneyService
from src.infra.deps import get_session
from src.infra.repos.account_repo import AccountRepo
from src.infra.repos.category_repo import CategoryRepo
from src.infra.repos.transaction_repo import TransactionRepo


def get_money_service(session: Session = Depends(get_session)) -> MoneyService:
    return MoneyService(
        transaction_repo=TransactionRepo(session=session),
        account_repo=AccountRepo(session=session),
        category_repo=CategoryRepo(session=session),
    )

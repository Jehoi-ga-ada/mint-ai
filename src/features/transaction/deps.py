from fastapi import Depends
from sqlalchemy.orm import Session

from src.features.transaction.service import TransactionService
from src.infra.deps import get_session
from src.infra.repos.transaction_repo import TransactionRepo


def get_transaction_repo(session: Session = Depends(get_session)):
    return TransactionRepo(session=session)


def get_transaction_service(repo: TransactionRepo = Depends(get_transaction_repo)):
    return TransactionService(repo=repo)

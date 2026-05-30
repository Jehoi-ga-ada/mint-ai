from fastapi import Depends
from sqlalchemy.orm import Session

from src.features.account.service import AccountService
from src.infra.deps import get_session
from src.infra.repos.account_repo import AccountRepo


def get_account_repo(session: Session = Depends(get_session)):
    return AccountRepo(session=session)


def get_account_service(repo: AccountRepo = Depends(get_account_repo)):
    return AccountService(repo=repo)

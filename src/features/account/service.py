from uuid import UUID

from src.features.account.starters import STARTER_ACCOUNTS
from src.infra.models.account import Account
from src.infra.repos.account_repo import AccountRepo


class AccountService:
    def __init__(self, repo: AccountRepo) -> None:
        self.repo = repo

    def create_starters(self, user_id: UUID) -> None:
        accounts = [Account(name=name, user_id=user_id) for name in STARTER_ACCOUNTS]
        self.repo.create_many(accounts)

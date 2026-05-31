from typing import Sequence
from uuid import UUID

from src.features.account.schema import AddAccount
from src.features.account.starters import STARTER_ACCOUNTS
from src.infra.models.account import Account
from src.infra.repos.account_repo import AccountRepo


class AccountService:
    def __init__(self, repo: AccountRepo) -> None:
        self.repo = repo

    def create_starters(self, user_id: UUID) -> None:
        accounts = [Account(name=name, user_id=user_id) for name in STARTER_ACCOUNTS]
        self.repo.create_many(accounts)

    def list_accounts(self, user_id: UUID) -> Sequence[Account]:
        return self.repo.list(order_by=Account.name, user_id=user_id)

    def create_account(self, payload: AddAccount, user_id: UUID) -> Account:
        account = Account(
            name=payload.name,
            type=payload.type,
            currency=payload.currency,
            institution=payload.institution,
            user_id=user_id,
        )
        return self.repo.create(account)

from uuid import UUID

from src.features.transaction.schema import AddTransaction
from src.infra.models.transaction import Transaction
from src.infra.repos.transaction_repo import TransactionRepo


class TransactionService:
    def __init__(self, repo: TransactionRepo) -> None:
        self.repo = repo

    def add_transaction(self, payload: AddTransaction, user_id: UUID):
        tx = Transaction(
            user_id=user_id,
            date=payload.date,
            currency=payload.currency,
            amount=payload.amount,
            type=payload.type,
            note=payload.note,
            category_id=payload.category_id,
            account_id=payload.account_id,
        )

        return self.repo.create(tx)

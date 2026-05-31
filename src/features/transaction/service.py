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

    def update_transaction(self, txn_id: UUID, payload: AddTransaction, user_id: UUID):
        tx = self._owned(txn_id, user_id)
        tx.date = payload.date
        tx.currency = payload.currency
        tx.amount = payload.amount
        tx.type = payload.type
        tx.note = payload.note
        tx.category_id = payload.category_id
        tx.account_id = payload.account_id
        return self.repo.update(tx)

    def delete_transaction(self, txn_id: UUID, user_id: UUID) -> None:
        self._owned(txn_id, user_id)
        self.repo.delete_by_id(txn_id)

    def _owned(self, txn_id: UUID, user_id: UUID) -> Transaction:
        tx = self.repo.get(txn_id)
        if tx is None or tx.user_id != user_id:
            raise ValueError("transaction_not_found")
        return tx

from sqlalchemy.orm import Session

from src.infra.models.transaction import Transaction
from src.shared.base_repo import BaseRepo


class TransactionRepo(BaseRepo[Transaction]):
    model = Transaction

    def __init__(self, session: Session) -> None:
        super().__init__(session)

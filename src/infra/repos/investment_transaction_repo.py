from sqlalchemy.orm import Session

from src.infra.models.investment_transaction import InvestmentTransaction
from src.shared.base_repo import BaseRepo


class InvestmentTransactionRepo(BaseRepo[InvestmentTransaction]):
    model = InvestmentTransaction

    def __init__(self, session: Session) -> None:
        super().__init__(session)

from sqlalchemy.orm import Session

from src.infra.models.account import Account
from src.shared.base_repo import BaseRepo


class AccountRepo(BaseRepo[Account]):
    model = Account

    def __init__(self, session: Session) -> None:
        super().__init__(session)

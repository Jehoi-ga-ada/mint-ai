from sqlalchemy.orm import Session

from src.infra.models.money_backup import MoneyBackup
from src.shared.base_repo import BaseRepo


class MoneyBackupRepo(BaseRepo[MoneyBackup]):
    model = MoneyBackup

    def __init__(self, session: Session) -> None:
        super().__init__(session)

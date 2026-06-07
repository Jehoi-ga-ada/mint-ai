from uuid import UUID

from src.infra.models.money_backup import MoneyBackup
from src.infra.repos.money_backup_repo import MoneyBackupRepo


class MoneyBackupService:
    """One snapshot blob per user, replaced wholesale on every upload."""

    def __init__(self, repo: MoneyBackupRepo) -> None:
        self.repo = repo

    def get(self, user_id: UUID) -> MoneyBackup | None:
        return self.repo.get_by(user_id=user_id)

    def put(self, user_id: UUID, data: str, schema_version: int) -> MoneyBackup:
        existing = self.repo.get_by(user_id=user_id)
        if existing is not None:
            existing.data = data
            existing.schema_version = schema_version
            return existing
        return self.repo.create(
            MoneyBackup(user_id=user_id, data=data, schema_version=schema_version)
        )

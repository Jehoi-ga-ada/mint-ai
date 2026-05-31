from sqlalchemy.orm import Session

from src.infra.models.asset import Asset
from src.shared.base_repo import BaseRepo


class AssetRepo(BaseRepo[Asset]):
    model = Asset

    def __init__(self, session: Session) -> None:
        super().__init__(session)

from sqlalchemy.orm import Session

from src.infra.models.fx_rate import FxRate
from src.shared.base_repo import BaseRepo


class FxRateRepo(BaseRepo[FxRate]):
    model = FxRate

    def __init__(self, session: Session) -> None:
        super().__init__(session)

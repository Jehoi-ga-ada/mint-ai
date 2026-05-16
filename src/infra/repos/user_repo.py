from sqlalchemy.orm import Session

from src.infra.models.user import User
from src.shared.base_repo import BaseRepo


class UserRepo(BaseRepo[User]):
    model = User

    def __init__(self, session: Session) -> None:
        super().__init__(session)

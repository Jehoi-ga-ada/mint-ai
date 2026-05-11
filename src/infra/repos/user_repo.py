from src.infra.models.user import User
from src.shared.base_repo import BaseRepo


class UserRepo(BaseRepo[User]):
    model = User

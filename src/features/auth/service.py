from src.infra.repos.user_repo import UserRepo
from src.shared.security import verify_password


class AuthService:
    def __init__(self, user_repo: UserRepo) -> None:
        self.user_repo = user_repo

    def auth_user(self, username: str, password: str):
        user = self.user_repo.get_by_username(username=username)

        if not user:
            return False

        if not verify_password(password, user.password_hash):
            return False

        return user

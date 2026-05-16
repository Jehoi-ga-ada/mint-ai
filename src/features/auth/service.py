from src.features.auth.schema import RegisterRequest
from src.infra.models.user import User
from src.infra.repos.user_repo import UserRepo
from src.shared.security import get_password_hash, verify_password


class AuthService:
    def __init__(self, user_repo: UserRepo) -> None:
        self.user_repo = user_repo

    def auth_user(self, username: str, password: str):
        user = self.user_repo.get_by(username=username)

        if not user:
            return False

        if not verify_password(password, user.password_hash):
            return False

        return user

    def register_user(self, data: RegisterRequest) -> User:
        if self.user_repo.exists(username=data.username):
            raise ValueError("username_taken")
        if self.user_repo.exists(email=data.email):
            raise ValueError("email_taken")

        user = User(
            username=data.username,
            email=data.email,
            password_hash=get_password_hash(password=data.password),
        )

        return self.user_repo.create(user)

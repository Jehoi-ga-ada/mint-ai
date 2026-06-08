from uuid import UUID

from sqlalchemy import delete as sa_delete
from sqlalchemy import select

from src.features.account.service import AccountService
from src.features.auth.schema import RegisterRequest
from src.features.category.service import CategoryService
from src.features.portfolio.service import PortfolioService
from src.infra.models.account import Account
from src.infra.models.category import Category
from src.infra.models.investment_transaction import InvestmentTransaction
from src.infra.models.money_backup import MoneyBackup
from src.infra.models.networth_snapshot import NetWorthSnapshot
from src.infra.models.portfolio import Portfolio
from src.infra.models.portfolio_snapshot import PortfolioSnapshot
from src.infra.models.transaction import Transaction
from src.infra.models.user import User
from src.infra.repos.user_repo import UserRepo
from src.shared.security import get_password_hash, verify_password


class AuthService:
    def __init__(
        self,
        user_repo: UserRepo,
        account_service: AccountService,
        category_service: CategoryService,
        portfolio_service: PortfolioService,
    ) -> None:
        self.user_repo = user_repo
        self.account_service = account_service
        self.category_service = category_service
        self.portfolio_service = portfolio_service

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
        user = self.user_repo.create(user)

        self.account_service.create_starters(user.id)
        self.category_service.create_starters(user.id)
        self.portfolio_service.create_starters(user.id)

        return user

    def delete_account(self, user_id: UUID) -> None:
        """Permanently delete the user and everything they own. Child rows are
        removed in FK-safe order (the relationships are WriteOnlyMapped with no
        DB-level cascade, and money_backups/portfolio_snapshots aren't covered
        by the ORM cascade at all)."""
        session = self.user_repo.session
        owned_portfolios = select(Portfolio.id).where(Portfolio.user_id == user_id)
        session.execute(
            sa_delete(PortfolioSnapshot).where(
                PortfolioSnapshot.portfolio_id.in_(owned_portfolios)
            )
        )
        for model in (
            InvestmentTransaction,
            Transaction,
            NetWorthSnapshot,
            MoneyBackup,
            Account,
            Category,
            Portfolio,
        ):
            session.execute(sa_delete(model).where(model.user_id == user_id))
        session.execute(sa_delete(User).where(User.id == user_id))

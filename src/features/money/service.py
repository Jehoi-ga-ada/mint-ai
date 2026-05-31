from collections import defaultdict
from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.features.money.schema import (
    AccountBalance,
    CategoryTotal,
    MoneyStats,
    MoneySummary,
    TransactionView,
)
from src.infra.models.transaction import Transaction, TypeEnum
from src.infra.repos.account_repo import AccountRepo
from src.infra.repos.category_repo import CategoryRepo
from src.infra.repos.transaction_repo import TransactionRepo

# Money manager is single-currency (IDR); no FX conversion.
CURRENCY = "IDR"
ZERO = Decimal(0)
DEFAULT_LEDGER_LIMIT = 100


class MoneyService:
    def __init__(
        self,
        transaction_repo: TransactionRepo,
        account_repo: AccountRepo,
        category_repo: CategoryRepo,
    ) -> None:
        self.transaction_repo = transaction_repo
        self.account_repo = account_repo
        self.category_repo = category_repo

    def list_transactions(
        self,
        user_id: UUID,
        txn_type: TypeEnum | None = None,
        account_id: UUID | None = None,
        start: date_type | None = None,
        end: date_type | None = None,
        limit: int = DEFAULT_LEDGER_LIMIT,
    ) -> list[TransactionView]:
        filters: dict = {"user_id": user_id}
        if txn_type is not None:
            filters["type"] = txn_type
        if account_id is not None:
            filters["account_id"] = account_id

        txns = [
            t
            for t in self.transaction_repo.list(
                order_by=Transaction.date.desc(), **filters
            )
            if _in_range(t.date, start, end)
        ][:limit]
        category_names = self._names(self.category_repo, user_id)
        account_names = self._names(self.account_repo, user_id)
        return [
            TransactionView(
                id=t.id,
                date=t.date,
                type=t.type,
                amount=t.amount,
                currency=t.currency,
                note=t.note,
                category_id=t.category_id,
                category_name=category_names.get(t.category_id, "—"),
                account_id=t.account_id,
                account_name=account_names.get(t.account_id, "—"),
            )
            for t in txns
        ]

    def summary(self, user_id: UUID) -> MoneySummary:
        txns = self.transaction_repo.list(user_id=user_id)
        balances: dict[UUID, Decimal] = defaultdict(lambda: ZERO)
        month_income = ZERO
        month_expense = ZERO
        month_start = self._month_start()

        for t in txns:
            signed = t.amount if t.type == TypeEnum.income else -t.amount
            balances[t.account_id] += signed
            if t.date >= month_start:
                if t.type == TypeEnum.income:
                    month_income += t.amount
                else:
                    month_expense += t.amount

        accounts = self.account_repo.list(user_id=user_id)
        account_balances = [
            AccountBalance(
                id=a.id,
                name=a.name,
                type=a.type,
                currency=a.currency,
                balance=balances.get(a.id, ZERO),
            )
            for a in accounts
        ]
        return MoneySummary(
            currency=CURRENCY,
            total_cash=sum((ab.balance for ab in account_balances), ZERO),
            month_income=month_income,
            month_expense=month_expense,
            accounts=account_balances,
        )

    def stats(
        self,
        user_id: UUID,
        txn_type: TypeEnum,
        start: date_type | None = None,
        end: date_type | None = None,
    ) -> MoneyStats:
        txns = [
            t
            for t in self.transaction_repo.list(user_id=user_id, type=txn_type)
            if _in_range(t.date, start, end)
        ]
        category_names = self._names(self.category_repo, user_id)

        by_category: dict[UUID, Decimal] = defaultdict(lambda: ZERO)
        total = ZERO
        for t in txns:
            total += t.amount
            by_category[t.category_id] += t.amount

        category_totals = sorted(
            (
                CategoryTotal(
                    category_id=cid,
                    category_name=category_names.get(cid, "—"),
                    total=amount,
                )
                for cid, amount in by_category.items()
            ),
            key=lambda c: c.total,
            reverse=True,
        )
        return MoneyStats(
            type=txn_type,
            currency=CURRENCY,
            total=total,
            by_category=category_totals,
        )

    @staticmethod
    def _names(repo, user_id: UUID) -> dict[UUID, str]:
        return {row.id: row.name for row in repo.list(user_id=user_id)}

    @staticmethod
    def _month_start() -> datetime:
        now = datetime.now()
        return datetime(now.year, now.month, 1)


def _in_range(
    moment: datetime, start: date_type | None, end: date_type | None
) -> bool:
    d = moment.date()
    if start is not None and d < start:
        return False
    if end is not None and d > end:
        return False
    return True

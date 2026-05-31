from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from src.features.money.service import MoneyService
from src.features.portfolio.service import PortfolioService
from src.infra.models.account import AccountType
from src.infra.models.asset import AssetClass
from src.infra.models.transaction import TypeEnum


# -- PortfolioService._summarize --------------------------------------------


def _holding(asset_class, market_value, cost_basis):
    return SimpleNamespace(
        asset_class=asset_class,
        market_value=Decimal(str(market_value)),
        cost_basis=Decimal(str(cost_basis)),
    )


def test_portfolio_summary_aggregates_value_cost_and_allocation():
    holdings = [
        _holding(AssetClass.crypto, 150, 100),
        _holding(AssetClass.metal, 50, 60),
    ]

    summary = PortfolioService._summarize(holdings)

    assert summary.total_value == Decimal(200)
    assert summary.total_cost == Decimal(160)
    assert summary.unrealized_pl == Decimal(40)
    assert summary.unrealized_pl_pct == Decimal(25)  # 40 / 160
    assert summary.allocation == {"crypto": Decimal(150), "metal": Decimal(50)}


def test_portfolio_summary_handles_empty_portfolio():
    summary = PortfolioService._summarize([])

    assert summary.total_value == Decimal(0)
    assert summary.total_cost == Decimal(0)
    assert summary.unrealized_pl_pct is None
    assert summary.allocation == {}


# -- MoneyService -----------------------------------------------------------


class FakeRepo:
    def __init__(self, rows):
        self.rows = rows

    def list(self, **kwargs):
        return self.rows


def _txn(amount, txn_type, account_id, category_id, date):
    return SimpleNamespace(
        id=uuid4(),
        amount=Decimal(str(amount)),
        type=txn_type,
        account_id=account_id,
        category_id=category_id,
        date=date,
        currency="IDR",
        note=None,
    )


def test_money_stats_groups_expense_by_category():
    food, transport = uuid4(), uuid4()
    txns = [
        _txn(100, TypeEnum.expense, uuid4(), food, datetime(2026, 5, 1)),
        _txn(50, TypeEnum.expense, uuid4(), food, datetime(2026, 4, 1)),
        _txn(30, TypeEnum.expense, uuid4(), transport, datetime(2026, 5, 2)),
    ]
    categories = [
        SimpleNamespace(id=food, name="Food"),
        SimpleNamespace(id=transport, name="Transport"),
    ]
    svc = MoneyService(
        transaction_repo=FakeRepo(txns),
        account_repo=FakeRepo([]),
        category_repo=FakeRepo(categories),
    )

    stats = svc.stats(user_id=uuid4(), txn_type=TypeEnum.expense)

    assert stats.total == Decimal(180)
    top = stats.by_category[0]
    assert (top.category_name, top.total) == ("Food", Decimal(150))
    # category percentages are derivable: Food is 150/180 of the total
    assert sum(c.total for c in stats.by_category) == stats.total


def test_money_stats_respects_date_range():
    from datetime import date

    food = uuid4()
    txns = [
        _txn(100, TypeEnum.expense, uuid4(), food, datetime(2026, 5, 10)),
        _txn(50, TypeEnum.expense, uuid4(), food, datetime(2026, 4, 1)),  # out of range
    ]
    svc = MoneyService(
        transaction_repo=FakeRepo(txns),
        account_repo=FakeRepo([]),
        category_repo=FakeRepo([SimpleNamespace(id=food, name="Food")]),
    )

    stats = svc.stats(
        user_id=uuid4(),
        txn_type=TypeEnum.expense,
        start=date(2026, 5, 1),
        end=date(2026, 5, 31),
    )

    assert stats.total == Decimal(100)  # April txn excluded


def test_money_summary_computes_balances_and_current_month():
    acc1, acc2 = uuid4(), uuid4()
    now = datetime.now()
    old = datetime(2000, 1, 1)
    txns = [
        _txn(1000, TypeEnum.income, acc1, uuid4(), now),
        _txn(200, TypeEnum.expense, acc1, uuid4(), now),
        _txn(500, TypeEnum.income, acc2, uuid4(), old),
    ]
    accounts = [
        SimpleNamespace(id=acc1, name="BCA", type=AccountType.bank, currency="IDR"),
        SimpleNamespace(id=acc2, name="Cash", type=AccountType.cash, currency="IDR"),
    ]
    svc = MoneyService(
        transaction_repo=FakeRepo(txns),
        account_repo=FakeRepo(accounts),
        category_repo=FakeRepo([]),
    )

    summary = svc.summary(user_id=uuid4())

    balances = {a.name: a.balance for a in summary.accounts}
    assert balances == {"BCA": Decimal(800), "Cash": Decimal(500)}
    assert summary.total_cash == Decimal(1300)
    assert summary.month_income == Decimal(1000)  # only this-month income
    assert summary.month_expense == Decimal(200)

from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

from src.features.holding.calc import compute_position, pct_return


def _txn(kind, qty, price, *, fee="0", currency="USD", day=1):
    return SimpleNamespace(
        type=kind,
        quantity=Decimal(str(qty)),
        price_per_unit=Decimal(str(price)),
        fee=Decimal(str(fee)),
        currency=currency,
        date=datetime(2026, 1, day),
    )


def test_single_buy_sets_quantity_and_avg_cost():
    pos = compute_position([_txn("buy", 2, 100)])

    assert pos.net_quantity == Decimal(2)
    assert pos.avg_cost == Decimal(100)
    assert pos.cost_basis_remaining == Decimal(200)
    assert pos.realized_pl == Decimal(0)
    assert pos.cost_currency == "USD"


def test_multiple_buys_average_cost():
    pos = compute_position([_txn("buy", 1, 100, day=1), _txn("buy", 1, 200, day=2)])

    assert pos.net_quantity == Decimal(2)
    assert pos.avg_cost == Decimal(150)
    assert pos.cost_basis_remaining == Decimal(300)


def test_buy_fee_increases_cost_basis():
    pos = compute_position([_txn("buy", 1, 100, fee=10)])

    assert pos.avg_cost == Decimal(110)
    assert pos.cost_basis_remaining == Decimal(110)


def test_sell_realizes_pl_against_average_cost():
    pos = compute_position([_txn("buy", 2, 100, day=1), _txn("sell", 1, 150, day=2)])

    assert pos.net_quantity == Decimal(1)
    assert pos.avg_cost == Decimal(100)  # avg cost unchanged by a sell
    assert pos.cost_basis_remaining == Decimal(100)
    assert pos.realized_pl == Decimal(50)  # (150 - 100) * 1


def test_full_exit_leaves_zero_quantity_and_realized_gain():
    pos = compute_position([_txn("buy", 1, 100, day=1), _txn("sell", 1, 120, day=2)])

    assert pos.net_quantity == Decimal(0)
    assert pos.cost_basis_remaining == Decimal(0)
    assert pos.realized_pl == Decimal(20)


def test_dividend_adds_to_realized_without_changing_quantity():
    pos = compute_position(
        [_txn("buy", 1, 100, day=1), _txn("dividend", 1, 5, day=2)]
    )

    assert pos.net_quantity == Decimal(1)
    assert pos.realized_pl == Decimal(5)


def test_transactions_processed_in_chronological_order():
    # Sell listed before buy but dated later — must still resolve correctly.
    pos = compute_position([_txn("sell", 1, 150, day=2), _txn("buy", 2, 100, day=1)])

    assert pos.net_quantity == Decimal(1)
    assert pos.realized_pl == Decimal(50)


def test_empty_history_is_flat():
    pos = compute_position([])

    assert pos.net_quantity == Decimal(0)
    assert pos.avg_cost == Decimal(0)
    assert pos.cost_currency is None


def test_pct_return():
    assert pct_return(Decimal(50), Decimal(200)) == Decimal(25)
    assert pct_return(Decimal(10), Decimal(0)) is None
    assert pct_return(Decimal(10), None) is None

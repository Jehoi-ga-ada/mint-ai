"""Pure portfolio math — average-cost position aggregation.

Decoupled from the ORM and network: every function takes plain values so it can
be unit-tested in isolation. `txns` items only need `.type`, `.quantity`,
`.price_per_unit`, `.fee`, `.currency`, and `.date` attributes.
"""

from dataclasses import dataclass
from decimal import Decimal

_BUY = {"buy", "transfer_in"}
_SELL = {"sell", "transfer_out"}
_INCOME = {"dividend", "interest"}
_FEE = {"fee"}

ZERO = Decimal(0)


@dataclass(frozen=True)
class Position:
    net_quantity: Decimal
    avg_cost: Decimal  # per-unit, in cost_currency
    cost_basis_remaining: Decimal  # net_quantity * avg_cost, in cost_currency
    realized_pl: Decimal  # in cost_currency
    cost_currency: str | None


def _type_of(txn) -> str:
    t = txn.type
    return t.value if hasattr(t, "value") else str(t)


def _dec(value) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value or 0))


def compute_position(txns) -> Position:
    """Aggregate one asset's transactions into a net position using average cost.

    Sells realize P/L against the running average cost. Dividends/interest add to
    realized P/L; standalone fees subtract from it.
    """
    qty = ZERO
    cost_total = ZERO
    realized = ZERO
    cost_currency: str | None = None

    for txn in sorted(txns, key=lambda t: t.date):
        kind = _type_of(txn)
        q = _dec(txn.quantity)
        price = _dec(txn.price_per_unit)
        fee = _dec(txn.fee)

        if cost_currency is None and kind in (_BUY | _SELL):
            cost_currency = txn.currency

        if kind in _BUY:
            qty += q
            cost_total += q * price + fee
        elif kind in _SELL:
            avg = (cost_total / qty) if qty > 0 else ZERO
            realized += q * (price - avg) - fee
            cost_total -= avg * q
            qty -= q
        elif kind in _INCOME:
            realized += q * price - fee
        elif kind in _FEE:
            realized -= q * price + fee

    has_qty = qty > 0
    avg_cost = (cost_total / qty) if has_qty else ZERO
    return Position(
        net_quantity=qty,
        avg_cost=avg_cost,
        cost_basis_remaining=cost_total if has_qty else ZERO,
        realized_pl=realized,
        cost_currency=cost_currency,
    )


def pct_return(profit: Decimal, cost_basis: Decimal) -> Decimal | None:
    """Simple return % = profit / cost_basis. None when there's no basis."""
    if cost_basis is None or cost_basis == 0:
        return None
    return (profit / cost_basis) * Decimal(100)

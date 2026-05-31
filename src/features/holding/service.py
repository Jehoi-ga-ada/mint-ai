from collections import defaultdict
from decimal import Decimal
from uuid import UUID

from src.features.holding.calc import Position, compute_position, pct_return
from src.features.holding.schema import (
    AddInvestmentTransaction,
    HoldingDetail,
    HoldingView,
    InvestmentTransactionView,
    PricePoint,
)
from src.features.pricing.service import PriceService
from src.infra.models.asset import Asset
from src.infra.models.investment_transaction import InvestmentTransaction
from src.infra.repos.asset_repo import AssetRepo
from src.infra.repos.investment_transaction_repo import InvestmentTransactionRepo
from src.infra.repos.portfolio_repo import PortfolioRepo

# Portfolios are USD-based; investment transactions and asset quotes are all USD,
# so valuation needs no FX conversion.
DISPLAY_CURRENCY = "USD"
ZERO = Decimal(0)


class HoldingService:
    def __init__(
        self,
        txn_repo: InvestmentTransactionRepo,
        asset_repo: AssetRepo,
        portfolio_repo: PortfolioRepo,
        price_service: PriceService,
    ) -> None:
        self.txn_repo = txn_repo
        self.asset_repo = asset_repo
        self.portfolio_repo = portfolio_repo
        self.price_service = price_service

    def add_transaction(
        self, payload: AddInvestmentTransaction, user_id: UUID
    ) -> InvestmentTransaction:
        portfolio = self.portfolio_repo.get(payload.portfolio_id)
        if portfolio is None or portfolio.user_id != user_id:
            raise ValueError("portfolio_not_found")

        txn = InvestmentTransaction(
            user_id=user_id,
            portfolio_id=payload.portfolio_id,
            asset_id=payload.asset_id,
            date=payload.date,
            type=payload.type,
            quantity=payload.quantity,
            price_per_unit=payload.price_per_unit,
            fee=payload.fee,
            currency=payload.currency,
            note=payload.note,
        )
        return self.txn_repo.create(txn)

    def list_transactions(self, portfolio_id: UUID) -> list[InvestmentTransactionView]:
        txns = self.txn_repo.list(
            order_by=InvestmentTransaction.date.desc(), portfolio_id=portfolio_id
        )
        symbols = {a.id: a.symbol for a in self.asset_repo.list()}
        return [
            InvestmentTransactionView(
                id=t.id,
                date=t.date,
                type=t.type,
                quantity=t.quantity,
                price_per_unit=t.price_per_unit,
                fee=t.fee,
                currency=t.currency,
                note=t.note,
                asset_id=t.asset_id,
                symbol=symbols.get(t.asset_id, "—"),
                portfolio_id=t.portfolio_id,
            )
            for t in txns
        ]

    def update_transaction(
        self, txn_id: UUID, payload: AddInvestmentTransaction, user_id: UUID
    ) -> InvestmentTransaction:
        txn = self._owned_txn(txn_id, user_id)
        txn.portfolio_id = payload.portfolio_id
        txn.asset_id = payload.asset_id
        txn.date = payload.date
        txn.type = payload.type
        txn.quantity = payload.quantity
        txn.price_per_unit = payload.price_per_unit
        txn.fee = payload.fee
        txn.currency = payload.currency
        txn.note = payload.note
        return self.txn_repo.update(txn)

    def delete_transaction(self, txn_id: UUID, user_id: UUID) -> None:
        self._owned_txn(txn_id, user_id)
        self.txn_repo.delete_by_id(txn_id)

    def _owned_txn(self, txn_id: UUID, user_id: UUID) -> InvestmentTransaction:
        txn = self.txn_repo.get(txn_id)
        if txn is None or txn.user_id != user_id:
            raise ValueError("transaction_not_found")
        return txn

    def list_holdings(self, portfolio_id: UUID) -> list[HoldingView]:
        positions = self._positions_by_asset(portfolio_id)
        views: list[HoldingView] = []
        for asset_id, pos in positions.items():
            if pos.net_quantity <= 0:
                continue
            asset = self.asset_repo.get(asset_id)
            if asset is None:
                continue
            views.append(self._build_view(asset, pos))
        return sorted(views, key=lambda v: v.market_value or ZERO, reverse=True)

    def get_holding(
        self, portfolio_id: UUID, asset_id: UUID
    ) -> HoldingDetail | None:
        asset = self.asset_repo.get(asset_id)
        if asset is None:
            return None
        txns = self.txn_repo.list(portfolio_id=portfolio_id, asset_id=asset_id)
        pos = compute_position(txns)
        view = self._build_view(asset, pos)
        history = [
            PricePoint(price=s.price, currency=s.currency, as_of=s.as_of)
            for s in self.price_service.history(asset)
        ]
        return HoldingDetail(**view.model_dump(), price_history=history)

    # -- internals -----------------------------------------------------------

    def _positions_by_asset(self, portfolio_id: UUID) -> dict[UUID, Position]:
        grouped: dict[UUID, list[InvestmentTransaction]] = defaultdict(list)
        for txn in self.txn_repo.list(portfolio_id=portfolio_id):
            grouped[txn.asset_id].append(txn)
        return {asset_id: compute_position(txns) for asset_id, txns in grouped.items()}

    def _build_view(self, asset: Asset, pos: Position) -> HoldingView:
        current_price = self.price_service.get_price(asset)
        price_available = current_price is not None

        market_value = pos.net_quantity * current_price if price_available else None
        cost_basis = pos.cost_basis_remaining

        unrealized_pl = None
        unrealized_pl_pct = None
        if market_value is not None:
            unrealized_pl = market_value - cost_basis
            unrealized_pl_pct = pct_return(unrealized_pl, cost_basis)

        return HoldingView(
            asset_id=asset.id,
            symbol=asset.symbol,
            name=asset.name,
            asset_class=asset.asset_class,
            quantity=pos.net_quantity,
            avg_cost=pos.avg_cost,
            cost_currency=pos.cost_currency,
            quote_currency=asset.quote_currency,
            current_price=current_price,
            price_available=price_available,
            display_currency=DISPLAY_CURRENCY,
            market_value=market_value,
            cost_basis=cost_basis,
            unrealized_pl=unrealized_pl,
            unrealized_pl_pct=unrealized_pl_pct,
            realized_pl=pos.realized_pl,
        )

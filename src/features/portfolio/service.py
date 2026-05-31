from collections import defaultdict
from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.features.holding.calc import pct_return
from src.features.holding.schema import HoldingView, InvestmentTransactionView
from src.features.holding.service import HoldingService
from src.features.portfolio.schema import (
    AddPortfolio,
    PortfolioDetail,
    PortfolioHistoryPoint,
    PortfolioSummary,
    PortfolioView,
)
from src.features.portfolio.starters import STARTER_PORTFOLIOS
from src.infra.models.portfolio import Portfolio
from src.infra.models.portfolio_snapshot import PortfolioSnapshot
from src.infra.repos.portfolio_repo import PortfolioRepo
from src.infra.repos.portfolio_snapshot_repo import PortfolioSnapshotRepo

ZERO = Decimal(0)


class PortfolioService:
    # holding_service / snapshot_repo are only needed for valuation; registration
    # seeds a starter portfolio with just the repo.
    def __init__(
        self,
        repo: PortfolioRepo,
        holding_service: HoldingService | None = None,
        snapshot_repo: PortfolioSnapshotRepo | None = None,
    ) -> None:
        self.repo = repo
        self.holding_service = holding_service
        self.snapshot_repo = snapshot_repo

    def create_starters(self, user_id: UUID) -> None:
        portfolios = [
            Portfolio(name=name, user_id=user_id) for name in STARTER_PORTFOLIOS
        ]
        self.repo.create_many(portfolios)

    def create(self, payload: AddPortfolio, user_id: UUID) -> Portfolio:
        portfolio = Portfolio(
            name=payload.name,
            base_currency=payload.base_currency,
            user_id=user_id,
        )
        return self.repo.create(portfolio)

    def list_with_summary(self, user_id: UUID) -> list[PortfolioView]:
        portfolios = self.repo.list(order_by=Portfolio.name, user_id=user_id)
        views: list[PortfolioView] = []
        for p in portfolios:
            summary = self._summarize(self.holding_service.list_holdings(p.id))
            self._capture(p.id, summary)
            views.append(
                PortfolioView(
                    id=p.id, name=p.name, base_currency=p.base_currency, summary=summary
                )
            )
        return views

    def get_detail(self, portfolio_id: UUID, user_id: UUID) -> PortfolioDetail | None:
        portfolio = self._owned(portfolio_id, user_id)
        if portfolio is None:
            return None
        holdings = self.holding_service.list_holdings(portfolio_id)
        summary = self._summarize(holdings)
        self._capture(portfolio_id, summary)
        return PortfolioDetail(
            id=portfolio.id,
            name=portfolio.name,
            base_currency=portfolio.base_currency,
            summary=summary,
            holdings=holdings,
        )

    def get_history(
        self,
        portfolio_id: UUID,
        user_id: UUID,
        start: date_type | None = None,
        end: date_type | None = None,
    ) -> list[PortfolioHistoryPoint] | None:
        if self._owned(portfolio_id, user_id) is None:
            return None
        rows = self.snapshot_repo.list(
            order_by=PortfolioSnapshot.date, portfolio_id=portfolio_id
        )
        return [
            PortfolioHistoryPoint(date=s.date, value=s.value)
            for s in rows
            if (start is None or s.date >= start) and (end is None or s.date <= end)
        ]

    def list_transactions(
        self, portfolio_id: UUID, user_id: UUID
    ) -> list[InvestmentTransactionView] | None:
        if self._owned(portfolio_id, user_id) is None:
            return None
        return self.holding_service.list_transactions(portfolio_id)

    def _owned(self, portfolio_id: UUID, user_id: UUID) -> Portfolio | None:
        portfolio = self.repo.get(portfolio_id)
        if portfolio is None or portfolio.user_id != user_id:
            return None
        return portfolio

    def _capture(self, portfolio_id: UUID, summary: PortfolioSummary) -> None:
        """Record today's value/cost (idempotent per day) to build trend history."""
        if self.snapshot_repo is None:
            return
        today = datetime.now().date()
        existing = self.snapshot_repo.get_by(portfolio_id=portfolio_id, date=today)
        if existing is not None:
            existing.value = summary.total_value
            existing.cost = summary.total_cost
            self.snapshot_repo.update(existing)
        else:
            self.snapshot_repo.create(
                PortfolioSnapshot(
                    portfolio_id=portfolio_id,
                    date=today,
                    value=summary.total_value,
                    cost=summary.total_cost,
                )
            )

    @staticmethod
    def _summarize(holdings: list[HoldingView]) -> PortfolioSummary:
        total_value = ZERO
        total_cost = ZERO
        allocation: dict[str, Decimal] = defaultdict(lambda: ZERO)
        for h in holdings:
            value = h.market_value or ZERO
            total_value += value
            total_cost += h.cost_basis or ZERO
            allocation[h.asset_class.value] += value
        unrealized = total_value - total_cost
        return PortfolioSummary(
            total_value=total_value,
            total_cost=total_cost,
            unrealized_pl=unrealized,
            unrealized_pl_pct=pct_return(unrealized, total_cost),
            allocation=dict(allocation),
        )

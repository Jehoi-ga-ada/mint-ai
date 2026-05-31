from fastapi import Depends
from sqlalchemy.orm import Session

from src.features.holding.service import HoldingService
from src.features.pricing.deps import get_price_service
from src.features.pricing.service import PriceService
from src.infra.deps import get_session
from src.infra.repos.asset_repo import AssetRepo
from src.infra.repos.investment_transaction_repo import InvestmentTransactionRepo
from src.infra.repos.portfolio_repo import PortfolioRepo


def get_holding_service(
    session: Session = Depends(get_session),
    price_service: PriceService = Depends(get_price_service),
) -> HoldingService:
    return HoldingService(
        txn_repo=InvestmentTransactionRepo(session=session),
        asset_repo=AssetRepo(session=session),
        portfolio_repo=PortfolioRepo(session=session),
        price_service=price_service,
    )

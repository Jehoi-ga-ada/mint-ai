from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.features.asset.deps import get_asset_service
from src.features.asset.schema import AssetPrice
from src.features.asset.service import AssetService
from src.features.auth.deps import get_current_user
from src.features.pricing.deps import get_price_service
from src.features.pricing.service import PriceService
from src.infra.models.user import User

router = APIRouter(prefix="/assets")


@router.get("")
def list_assets(
    service: AssetService = Depends(get_asset_service),
    user: User = Depends(get_current_user),
):
    return service.list_assets()


@router.get("/{asset_id}/price")
def get_asset_price(
    asset_id: UUID,
    service: AssetService = Depends(get_asset_service),
    price_service: PriceService = Depends(get_price_service),
    user: User = Depends(get_current_user),
) -> AssetPrice:
    asset = service.get(asset_id)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="asset_not_found"
        )
    price = price_service.get_price(asset)
    return AssetPrice(
        asset_id=str(asset.id),
        symbol=asset.symbol,
        price=price,
        currency=asset.quote_currency,
        available=price is not None,
    )

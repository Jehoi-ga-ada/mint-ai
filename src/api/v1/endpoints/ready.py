from fastapi import APIRouter, Depends

from src.features.readiness import Ready
from src.features.readiness.deps import get_ready_service
from src.features.readiness.service import CheckReadyService
from src.shared.base_response import APIResponse

router = APIRouter()


@router.get("/ready", response_model=APIResponse[Ready])
def ready(
    check_ready_service: CheckReadyService = Depends(get_ready_service),
):
    ready = check_ready_service.ready()
    return APIResponse.success(data=ready)

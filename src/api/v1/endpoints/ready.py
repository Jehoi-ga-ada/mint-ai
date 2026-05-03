from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.features.readiness import Ready
from src.features.readiness.service import CheckReadyService
from src.infra.container import Container
from src.shared.base_response import APIResponse

router = APIRouter()


@router.get("/ready", response_model=APIResponse[Ready])
@inject
def ready(
    checkReadyService: CheckReadyService = Depends(
        Provide[Container.checkReadyService]
    ),
):
    ready = checkReadyService.ready()
    return APIResponse.success(data=ready)

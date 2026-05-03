from fastapi import APIRouter

from src.shared.base_response import APIResponse

router = APIRouter()


@router.get("/health", response_model=APIResponse[str])
def healthcheck():
    return APIResponse.success(data="healthy")

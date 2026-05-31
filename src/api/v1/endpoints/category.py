from fastapi import APIRouter, Depends

from src.features.auth.deps import get_current_user
from src.features.category.deps import get_category_service
from src.features.category.schema import AddCategory
from src.features.category.service import CategoryService
from src.infra.models.category import CategoryKind
from src.infra.models.user import User

router = APIRouter(prefix="/categories")


@router.get("")
def list_categories(
    kind: CategoryKind | None = None,
    service: CategoryService = Depends(get_category_service),
    user: User = Depends(get_current_user),
):
    return service.list_categories(user_id=user.id, kind=kind)


@router.post("")
def create_category(
    payload: AddCategory,
    service: CategoryService = Depends(get_category_service),
    user: User = Depends(get_current_user),
):
    return service.create_category(name=payload.name, kind=payload.kind, user_id=user.id)

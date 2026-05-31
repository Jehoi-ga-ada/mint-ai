from pydantic import BaseModel

from src.infra.models.category import CategoryKind


class AddCategory(BaseModel):
    name: str
    kind: CategoryKind = CategoryKind.expense

from typing import Sequence
from uuid import UUID

from src.features.category.starters import (
    STARTER_EXPENSE_CATEGORIES,
    STARTER_INCOME_CATEGORIES,
)
from src.infra.models.category import Category, CategoryKind
from src.infra.repos.category_repo import CategoryRepo


class CategoryService:
    def __init__(self, repo: CategoryRepo) -> None:
        self.repo = repo

    def create_starters(self, user_id: UUID) -> None:
        categories = [
            Category(name=name, kind=CategoryKind.expense, user_id=user_id)
            for name in STARTER_EXPENSE_CATEGORIES
        ] + [
            Category(name=name, kind=CategoryKind.income, user_id=user_id)
            for name in STARTER_INCOME_CATEGORIES
        ]
        self.repo.create_many(categories)

    def list_categories(
        self, user_id: UUID, kind: CategoryKind | None = None
    ) -> Sequence[Category]:
        filters: dict = {"user_id": user_id}
        if kind is not None:
            filters["kind"] = kind
        return self.repo.list(order_by=Category.name, **filters)

    def create_category(
        self, name: str, kind: CategoryKind, user_id: UUID
    ) -> Category:
        category = Category(name=name, kind=kind, user_id=user_id)
        return self.repo.create(category)

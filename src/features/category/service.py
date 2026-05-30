from uuid import UUID

from src.features.category.starters import STARTER_CATEGORIES
from src.infra.models.category import Category
from src.infra.repos.category_repo import CategoryRepo


class CategoryService:
    def __init__(self, repo: CategoryRepo) -> None:
        self.repo = repo

    def create_starters(self, user_id: UUID) -> None:
        categories = [
            Category(name=name, user_id=user_id) for name in STARTER_CATEGORIES
        ]
        self.repo.create_many(categories)

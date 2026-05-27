from sqlalchemy.orm import Session

from src.infra.models.category import Category
from src.shared.base_repo import BaseRepo


class CategoryRepo(BaseRepo[Category]):
    model = Category

    def __init__(self, session: Session) -> None:
        super().__init__(session)

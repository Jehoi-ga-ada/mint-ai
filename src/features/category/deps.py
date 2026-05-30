from fastapi import Depends
from sqlalchemy.orm import Session

from src.features.category.service import CategoryService
from src.infra.deps import get_session
from src.infra.repos.category_repo import CategoryRepo


def get_category_repo(session: Session = Depends(get_session)):
    return CategoryRepo(session=session)


def get_category_service(repo: CategoryRepo = Depends(get_category_repo)):
    return CategoryService(repo=repo)

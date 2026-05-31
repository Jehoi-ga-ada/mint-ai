from fastapi import Depends
from sqlalchemy.orm import Session

from src.features.asset.service import AssetService
from src.infra.deps import get_session
from src.infra.repos.asset_repo import AssetRepo


def get_asset_repo(session: Session = Depends(get_session)):
    return AssetRepo(session=session)


def get_asset_service(repo: AssetRepo = Depends(get_asset_repo)):
    return AssetService(repo=repo)

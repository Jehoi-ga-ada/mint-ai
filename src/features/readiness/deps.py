from fastapi import Depends
from sqlalchemy.orm import Session

from src.features.readiness.service import CheckReadyService
from src.infra.deps import get_session


def get_ready_service(session: Session = Depends(get_session)) -> CheckReadyService:
    return CheckReadyService(session)

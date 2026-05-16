from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from src.features.auth.schema import TokenData, User
from src.features.auth.service import AuthService
from src.infra.config import config
from src.infra.deps import get_session
from src.infra.repos.user_repo import UserRepo

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def get_user_repo(session: Session = Depends(get_session)):
    return UserRepo(session=session)


def get_auth_service(user_repo: UserRepo = Depends(get_user_repo)):
    return AuthService(user_repo=user_repo)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repo: UserRepo = Depends(get_user_repo),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, config.secret_key, algorithms=[config.algorithm])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception

    user = user_repo.get_by(username=token_data.username)

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

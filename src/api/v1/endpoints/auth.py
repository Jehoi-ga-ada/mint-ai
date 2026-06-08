from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.features.auth.deps import get_auth_service, get_current_user
from src.features.auth.schema import RegisterRequest, Token, User
from src.features.auth.service import AuthService
from src.infra.config import config
from src.infra.models.user import User as UserModel
from src.shared.security import create_access_token

router = APIRouter(prefix="/auth")


@router.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    user = auth_service.auth_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=config.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/register")
def register(
    payload: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    try:
        return auth_service.register_user(payload)
    except ValueError as e:
        if str(e) == "username_taken":
            raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken")
        if str(e) == "email_taken":
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
        raise


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(
    auth_service: AuthService = Depends(get_auth_service),
    current_user: UserModel = Depends(get_current_user),
) -> None:
    auth_service.delete_account(current_user.id)

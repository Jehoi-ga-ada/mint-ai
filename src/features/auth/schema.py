from uuid import UUID

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    id: UUID
    username: str
    email: str | None = None
    disabled: bool


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

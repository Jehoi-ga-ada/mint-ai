from typing import Generic, Optional, TypeVar

from fastapi import status
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    code: int
    status: str
    message: Optional[str] = None
    data: Optional[T] = None

    @classmethod
    def success(cls, data: T, message: str = "Success"):
        return cls(
            code=status.HTTP_200_OK,
            status="OK",
            message=message,
            data=data,
        )

    @classmethod
    def error(
        cls,
        message: str = "Internal Server Error",
        code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        return cls(
            code=code,
            status="Error",
            message=message,
        )

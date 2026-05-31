from pydantic import BaseModel

from src.infra.models.account import AccountType


class AddAccount(BaseModel):
    name: str
    type: AccountType = AccountType.bank
    currency: str = "IDR"
    institution: str | None = None

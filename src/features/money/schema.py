from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from src.infra.models.account import AccountType
from src.infra.models.transaction import TypeEnum


class TransactionView(BaseModel):
    id: UUID
    date: datetime
    type: TypeEnum
    amount: Decimal
    currency: str
    note: str | None
    category_id: UUID
    category_name: str
    account_id: UUID
    account_name: str


class AccountBalance(BaseModel):
    id: UUID
    name: str
    type: AccountType
    currency: str
    balance: Decimal


class MoneySummary(BaseModel):
    currency: str
    total_cash: Decimal
    month_income: Decimal
    month_expense: Decimal
    accounts: list[AccountBalance]


class CategoryTotal(BaseModel):
    category_id: UUID | None
    category_name: str
    total: Decimal


class MoneyStats(BaseModel):
    type: TypeEnum
    currency: str
    total: Decimal
    by_category: list[CategoryTotal]


# 2MB of JSON — far above any realistic personal ledger, bounds request size.
MAX_BACKUP_CHARS = 2_000_000


class MoneyBackupIn(BaseModel):
    data: str = Field(min_length=2, max_length=MAX_BACKUP_CHARS)
    schema_version: int = Field(ge=1)


class MoneyBackupOut(BaseModel):
    data: str
    schema_version: int
    updated_at: datetime

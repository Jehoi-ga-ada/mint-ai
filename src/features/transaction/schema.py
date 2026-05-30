from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from src.infra.models.transaction import TypeEnum


class AddTransaction(BaseModel):
    date: datetime
    currency: str
    amount: Decimal
    type: TypeEnum
    account_id: UUID
    category_id: UUID
    note: str | None

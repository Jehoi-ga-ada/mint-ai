"""Idempotent create: replaying a queued offline transaction (same client_id)
must not insert a second row."""

from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from src.features.transaction.schema import AddTransaction
from src.features.transaction.service import TransactionService
from src.infra.models.transaction import TypeEnum


class FakeRepo:
    """Minimal repo standing in for TransactionRepo: stores created rows and
    supports get_by(user_id=, client_id=) like BaseRepo."""

    def __init__(self):
        self.rows = []

    def get_by(self, **filters):
        for row in self.rows:
            if all(getattr(row, k) == v for k, v in filters.items()):
                return row
        return None

    def create(self, entity):
        self.rows.append(entity)
        return entity


def _payload(client_id=None):
    return AddTransaction(
        date=datetime(2026, 6, 1),
        currency="IDR",
        amount=Decimal("100"),
        type=TypeEnum.expense,
        account_id=uuid4(),
        category_id=uuid4(),
        note="coffee",
        client_id=client_id,
    )


def test_replaying_same_client_id_returns_existing_row():
    # Arrange
    repo = FakeRepo()
    svc = TransactionService(repo)
    user_id = uuid4()
    payload = _payload(client_id="offline-abc-123")

    # Act — same payload submitted twice (the replay)
    first = svc.add_transaction(payload=payload, user_id=user_id)
    second = svc.add_transaction(payload=payload, user_id=user_id)

    # Assert — only one row persisted, both calls return it
    assert len(repo.rows) == 1
    assert first is second
    assert first.client_id == "offline-abc-123"


def test_missing_client_id_always_inserts():
    # Arrange
    repo = FakeRepo()
    svc = TransactionService(repo)
    user_id = uuid4()

    # Act — two online creates with no client_id
    svc.add_transaction(payload=_payload(), user_id=user_id)
    svc.add_transaction(payload=_payload(), user_id=user_id)

    # Assert — both inserted (NULL client_id is not de-duped)
    assert len(repo.rows) == 2


def test_different_users_same_client_id_are_independent():
    # Arrange
    repo = FakeRepo()
    svc = TransactionService(repo)

    # Act — same client_id, different users
    svc.add_transaction(payload=_payload(client_id="dup"), user_id=uuid4())
    svc.add_transaction(payload=_payload(client_id="dup"), user_id=uuid4())

    # Assert — scoped per user, so both insert
    assert len(repo.rows) == 2

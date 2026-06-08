"""delete_account must remove every user-owned table in FK-safe order
(children before parents), since the ORM cascades are WriteOnlyMapped with no
DB-level ON DELETE and money_backups/portfolio_snapshots aren't covered."""

from uuid import uuid4

from src.features.auth.service import AuthService


class FakeSession:
    def __init__(self):
        self.deleted_tables: list[str] = []

    def execute(self, stmt):
        # sa_delete(Model) statements expose the target Table.
        self.deleted_tables.append(stmt.table.name)


class FakeUserRepo:
    def __init__(self, session):
        self.session = session


def test_deletes_all_user_tables_in_fk_safe_order():
    session = FakeSession()
    auth = AuthService(
        user_repo=FakeUserRepo(session),
        account_service=None,
        category_service=None,
        portfolio_service=None,
    )

    auth.delete_account(uuid4())

    order = session.deleted_tables
    # Every user-owned table is cleared, users last.
    assert set(order) == {
        "portfolio_snapshots",
        "investment_transactions",
        "transactions",
        "networth_snapshots",
        "money_backups",
        "accounts",
        "categories",
        "portfolios",
        "users",
    }
    assert order[-1] == "users"
    # Snapshots before the portfolios they reference; portfolios before users.
    assert order.index("portfolio_snapshots") < order.index("portfolios")
    assert order.index("investment_transactions") < order.index("portfolios")
    assert order.index("portfolios") < order.index("users")

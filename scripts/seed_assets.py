"""Seed the shared asset catalog. Run with: `make seed` or `uv run python -m scripts.seed_assets`."""

from src.features.asset.service import AssetService
from src.infra.config import config
from src.infra.database import PostgreDatabase
from src.infra.repos.asset_repo import AssetRepo


def main() -> None:
    db = PostgreDatabase(db_url=config.db_url)
    session = db._session_factory()
    try:
        created = AssetService(repo=AssetRepo(session=session)).seed_catalog()
        session.commit()
        print(f"Seeded {created} new asset(s).")
    finally:
        session.close()


if __name__ == "__main__":
    main()

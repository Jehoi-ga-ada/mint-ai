.PHONY: help upgrade create-migration seed

help:
	@echo "Available commands:"
	@echo "  make upgrade          - Run migrations"
	@echo "  make create-migration - Generate new migration"
	@echo "  make seed             - Seed the shared asset catalog"

upgrade:
	uv run alembic upgrade head

create-migration:
	uv run alembic revision --autogenerate -m "$(m)"

seed:
	uv run python -m scripts.seed_assets

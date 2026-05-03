.PHONY: help upgrade create-migration

help:
	@echo "Available commands:"
	@echo "  make upgrade          - Run migrations"
	@echo "  make create-migration - Generate new migration"

upgrade: 
	uv run alembic upgrade head

create-migration:
	uv run alembic revision --autogenerate -m "$(m)"

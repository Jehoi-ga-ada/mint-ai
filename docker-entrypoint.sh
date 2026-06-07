#!/bin/sh
# Apply migrations and seed the (idempotent) asset catalog before serving.
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Seeding asset catalog..."
python -m scripts.seed_assets

exec "$@"

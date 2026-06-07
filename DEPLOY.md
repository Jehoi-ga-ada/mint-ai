# Deploying the backend with Docker

The image is published to GHCR, so a server only ever needs **two files**:
`compose.yaml` and `.env`.

## 1. Build & push (from your machine, or CI later)

```sh
docker build -t ghcr.io/jehoi-ga-ada/mint-ai:latest .
docker push ghcr.io/jehoi-ga-ada/mint-ai:latest
```

(One-time: `docker login ghcr.io -u jehoi-ga-ada` with a GitHub PAT that has
`write:packages`.)

## 2. Server setup (once)

```sh
docker login ghcr.io -u jehoi-ga-ada   # PAT with read:packages
```

Copy `compose.yaml` and your `.env` to the server. On top of the usual app
keys (see `.env.example`), `.env` must define the Postgres bootstrap values —
they MUST match the credentials inside `DB_URL`:

```sh
POSTGRES_USER=mint_ai_user
POSTGRES_PASSWORD=<same password as in DB_URL>
POSTGRES_DB=mint_ai_db
# and DB_URL points at the compose service name:
# DB_URL=postgresql+psycopg2://mint_ai_user:<password>@db:5432/mint_ai_db
```

## 3. Run

```sh
docker compose up -d
```

On startup the API container applies migrations (`alembic upgrade head`) and
seeds the asset catalog (idempotent) before serving on port 8080 with 2
uvicorn workers. Postgres data persists in the `pgdata` volume.

## 4. Update to a new version

```sh
docker compose pull && docker compose up -d
```

## Notes

- TLS/reverse-proxy (nginx) is intentionally outside this compose file —
  pair it with the terraform/nginx setup.
- Logs: `docker compose logs -f api`
- The healthcheck hits `/api/v1/health`; `docker compose ps` shows status.

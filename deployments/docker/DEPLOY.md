# Deploying the backend with Docker

The image is published to GHCR, so a server only ever needs **two files**:
`docker-compose.yaml` and `.env`.

## 1. Build & push (from your machine, or CI later)

From the repo root:

```sh
docker build -f deployments/docker/Dockerfile -t ghcr.io/jehoi-ga-ada/mint-ai:latest .
docker push ghcr.io/jehoi-ga-ada/mint-ai:latest
```

(One-time: `docker login ghcr.io -u jehoi-ga-ada` with a GitHub PAT that has
`write:packages`.)

## 2. Server setup (once)

```sh
docker login ghcr.io -u jehoi-ga-ada   # PAT with read:packages
```

Copy `docker-compose.yaml` and your `.env` into one directory on the server.
On top of the usual app keys (see `.env.example`), `.env` must define:

```sh
POSTGRES_USER=mint_ai_user
POSTGRES_PASSWORD=<password>
POSTGRES_DB=mint_ai_db
```

The API's `DB_URL` is composed inside the compose file from these values
(pointing at the `db` service), so the `DB_URL` in `.env` — e.g. localhost for
local runs — is ignored inside compose.

## 3. Run

```sh
docker compose pull && docker compose up -d
```

On startup the API container applies migrations (`alembic upgrade head`) and
seeds the asset catalog (idempotent) before serving on port 8080 with 2
uvicorn workers. Postgres data persists in the `postgres_data` volume and is
reachable only from the API container (no host port).

## 4. Update to a new version

```sh
docker compose pull && docker compose up -d
```

## Local build-from-source

From `deployments/docker/` with the repo checked out (`.env` here is a
git-ignored symlink to the repo-root `.env` — recreate with
`ln -s ../../.env .env` if missing):

```sh
docker compose up -d --build
```

## Notes

- TLS/reverse-proxy (nginx) is intentionally outside this compose file —
  pair it with the terraform/nginx setup.
- Logs: `docker compose logs -f mint-backend`
- The image healthcheck hits `/api/v1/health`; `docker compose ps` shows it.

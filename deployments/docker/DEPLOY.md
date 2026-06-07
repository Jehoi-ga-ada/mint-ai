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

Copy `nginx.conf` and `init-tls.sh` alongside the compose file (four files
total). Make sure the DNS name (mintai.eastasia.cloudapp.azure.com) resolves
to this server and ports 80 + 443 are open, then — **first boot only** —
issue the certificate before starting the stack:

```sh
sh init-tls.sh you@example.com   # email optional: gets LE expiry notices
```

That obtains the Let's Encrypt cert on a free port 80, then brings the whole
stack up. Every boot after that is just:

```sh
docker compose pull && docker compose up -d
```

The certbot sidecar renews the cert automatically (checks every 12h; LE certs
last 90 days and renew at 60) and nginx reloads itself every 6h to pick up
rotated certs.

nginx is the only public entry point: port 80 answers ACME challenges and
301-redirects everything else to HTTPS; port 443 terminates TLS
(TLS 1.2/1.3) and proxies `/api/` to the backend with per-IP rate limits:

| Route | Limit | Why |
|---|---|---|
| `/api/v1/auth/` | 10/min, burst 10 | login/register brute force |
| `/api/v1/chat/` | 30/min, burst 5 | LLM quota burn; buffering off for SSE, 40MB bodies for image messages |
| `/api/` (rest) | 10/s, burst 20 | general protection |

Anything outside `/api/` returns 404. The API container has no published
port — traffic can only enter through nginx.

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

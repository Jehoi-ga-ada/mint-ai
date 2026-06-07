# Build from the repo root:
#   docker build -f deployments/docker/Dockerfile -t ghcr.io/jehoi-ga-ada/mint-ai:latest .

# ── Builder: resolve and install dependencies with uv ────────────────────────
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1

WORKDIR /app

# Dependency layer first — rebuilt only when the lockfile changes, not on
# every source edit.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

# ── Runtime: slim image with just the venv and the source ────────────────────
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Run as a non-root user.
RUN groupadd -r app && useradd -r -g app app

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY alembic.ini main.py ./
COPY migrations ./migrations
COPY scripts ./scripts
COPY src ./src
COPY deployments/docker/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh && chown -R app:app /app

USER app
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/api/v1/health', timeout=4)"

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]

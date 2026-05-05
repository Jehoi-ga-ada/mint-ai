FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /uvx /bin/

WORKDIR /app

COPY . /app
ENV UV_NO_DEV=1

RUN uv sync --locked
CMD ["uv", "run", "main.py"]

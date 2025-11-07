FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

WORKDIR /code

COPY pyproject.toml uv.lock /code

RUN uv sync

COPY server/src /code/app

CMD ["uv", "run", "fastapi", "run", "app/main.py", "--port", "80"]

FROM python:3.12-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /app

WORKDIR /app

RUN uv sync --locked

ENTRYPOINT ["uv", "run", "python", "main.py"]
CMD []
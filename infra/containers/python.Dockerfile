FROM ghcr.io/astral-sh/uv:0.12.18 AS uv
FROM python:3.12.14-alpine3.24
COPY --from=uv /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY apps/api apps/api
COPY apps/worker apps/worker
COPY apps/__init__.py apps/__init__.py
COPY services services
RUN adduser -D -u 10001 kasoma && chown -R kasoma:kasoma /app
USER kasoma
ENV UV_NO_SYNC=1 PYTHONUNBUFFERED=1
CMD ["uv", "run", "uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--no-access-log"]

FROM python:3.13-slim AS build

ENV UV_LINK_MODE=copy
WORKDIR /app

RUN python -m pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project


FROM python:3.13-slim AS run

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/app/.venv

WORKDIR /app

RUN useradd --system --create-home --shell /usr/sbin/nologin appuser
RUN chown -R appuser:appuser /app

COPY --from=build --chown=appuser:appuser /app/.venv /app/.venv
COPY --chown=appuser:appuser adapter /app/adapter
COPY --chown=appuser:appuser config /app/config
COPY --chown=appuser:appuser domain /app/domain
COPY --chown=appuser:appuser repository /app/repository
COPY --chown=appuser:appuser usecase /app/usecase
COPY --chown=appuser:appuser main.py /app/main.py
COPY --chown=appuser:appuser manage.py /app/manage.py
COPY --chown=appuser:appuser entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

USER appuser

EXPOSE 8123

ENTRYPOINT /app/entrypoint.sh

# syntax=docker/dockerfile:1
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=ghcr.io/astral-sh/uv:0.12.5 /uv /uvx /usr/local/bin/

WORKDIR /app

# Install dependencies first so dependency layers are cached independently
# of application code changes.
COPY Code/pyproject.toml Code/uv.lock ./
RUN uv sync --frozen --no-install-project

COPY Code/manage.py ./
COPY Code/config ./config
COPY Code/event_in_a_box ./event_in_a_box
COPY Code/templates ./templates
COPY Code/static ./static
COPY Code/tests ./tests

RUN uv sync --frozen

# Static assets are collected at build time. Settings fall back to safe,
# non-production defaults when no environment variables are supplied, so no
# real secret is required for this step.
RUN python manage.py collectstatic --noinput

RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]

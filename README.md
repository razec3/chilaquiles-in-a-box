# Event in a Box

Event in a Box helps restaurateurs plan an economically sensible Apero for an
event in a few minutes. This repository currently contains the **technical
foundation only** — Django, PostgreSQL, Gunicorn, Nginx, Docker Compose, and
the test and CI setup. Business features are added only after their feature
specifications under `Documentation/specs/` are approved. See [CLAUDE.md](CLAUDE.md) for
the full project scope and engineering rules.

## Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose v2
- Git

Local Python tooling ([uv](https://docs.astral.sh/uv/)) is only needed if you
want to run commands outside Docker.

## Getting started

Clone the repository and move into it:

```bash
git clone <repository-url>
cd chilaquiles-in-a-box
```

Create your local environment file:

```bash
cp .env.example .env
```

Build the containers:

```bash
docker compose build
```

Run database migrations (an explicit step, never run automatically on
container start):

```bash
docker compose run --rm web python manage.py migrate
```

Start the stack:

```bash
docker compose up
```

Open the application at [http://localhost:8080](http://localhost:8080) and
the health endpoint at [http://localhost:8080/health/](http://localhost:8080/health/).

Stop the stack:

```bash
docker compose down
```

Remove local development volumes (database data, collected static files)
when explicitly desired:

```bash
docker compose down -v
```

## Running tests

All tests run inside the `web` container against the real PostgreSQL
service defined in `compose.yaml`.

Run the full suite:

```bash
docker compose run --rm web pytest
```

Run each test category separately:

```bash
docker compose run --rm web pytest tests/unit
docker compose run --rm web pytest tests/integration
docker compose run --rm web pytest tests/acceptance
```

## Formatting and linting

```bash
docker compose run --rm web ruff format --check .
docker compose run --rm web ruff check .
```

## Django checks

```bash
docker compose run --rm web python manage.py check
docker compose run --rm web python manage.py makemigrations --check --dry-run
```

## Working outside Docker (optional)

From `Code/`, using [uv](https://docs.astral.sh/uv/):

```bash
cd Code
uv sync --frozen
uv run pytest tests/unit
```

Integration and acceptance tests require a reachable PostgreSQL instance
matching the `POSTGRES_*` variables in `.env`.

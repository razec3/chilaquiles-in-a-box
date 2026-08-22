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

Static files (including the Django admin's own CSS/JS) are collected into
the image at build time, but the `web`/`nginx` containers share them through
a named volume that is only auto-populated from the image the *first* time
it's created. After a rebuild that changes static assets, refresh the shared
volume explicitly:

```bash
docker compose run --rm web python manage.py collectstatic --noinput
```

Create an admin account (see "Django admin" below):

```bash
docker compose run --rm web python manage.py createsuperuser
```

Start the stack:

```bash
docker compose up
```

Open the application at [http://localhost:8080](http://localhost:8080), the
health endpoint at [http://localhost:8080/health/](http://localhost:8080/health/),
and the admin panel at [http://localhost:8080/admin/](http://localhost:8080/admin/).

Stop the stack:

```bash
docker compose down
```

Remove local development volumes (database data, collected static files)
when explicitly desired:

```bash
docker compose down -v
```

## Django admin

The admin panel manages master data directly in PostgreSQL: Products,
Recipes (with their ingredients, added inline), Event types, and
Preferences. It is standalone infrastructure for now — the Working
Skeleton feature (`specs/001-working-skeleton`) still reads its own mock
data from `Code/event_in_a_box/mock_data.py`, not this database, so
entries added here don't yet affect that flow.

Create an account, then log in at
[http://localhost:8080/admin/](http://localhost:8080/admin/):

```bash
docker compose run --rm web python manage.py createsuperuser
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

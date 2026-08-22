#!/usr/bin/env sh
# Explicit, documented migration step. Migrations are never run
# automatically by the web container's startup command.
set -eu

docker compose run --rm web python manage.py migrate

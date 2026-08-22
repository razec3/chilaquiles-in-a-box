"""Integration test proving Django can connect to PostgreSQL."""

import pytest
from django.db import connection

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_django_can_connect_to_postgresql():
    connection.ensure_connection()

    assert connection.vendor == "postgresql"

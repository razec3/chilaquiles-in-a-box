"""Unit test for the deterministic /health/ response.

Does not require a PostgreSQL connection: the health view performs no
database access.
"""

import json

import pytest

pytestmark = pytest.mark.unit


def test_health_endpoint_returns_deterministic_ok_payload(client):
    response = client.get("/health/")

    assert response.status_code == 200
    assert json.loads(response.content) == {"status": "ok"}

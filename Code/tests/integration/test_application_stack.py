"""Integration tests proving the configured Django application loads."""

import json

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_health_endpoint_returns_http_200(client):
    response = client.get("/health/")

    assert response.status_code == 200
    assert json.loads(response.content) == {"status": "ok"}


@pytest.mark.django_db
def test_start_page_loads_successfully(client):
    response = client.get("/")

    assert response.status_code == 200

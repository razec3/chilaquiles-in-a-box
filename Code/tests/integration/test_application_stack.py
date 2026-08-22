"""Integration tests proving the configured Django application loads."""

import json

import pytest
from django.test import Client
from django.urls import reverse

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


@pytest.mark.django_db
def test_post_requests_through_the_nginx_origin_are_not_blocked_by_csrf():
    # Regression test: nginx forwards the app on http://localhost:8080, a
    # different origin than Django's own host:port. Without
    # DJANGO_CSRF_TRUSTED_ORIGINS covering it, every POST form submission
    # fails Django's CSRF Origin check even with a valid token. The default
    # Django test Client doesn't enforce CSRF at all, so this needs its own
    # strict client to actually exercise the check.
    strict_client = Client(enforce_csrf_checks=True)
    get_response = strict_client.get(reverse("event_in_a_box:event_input"))
    csrf_token = get_response.cookies["csrftoken"].value

    response = strict_client.post(
        reverse("event_in_a_box:event_input"),
        {"guest_count": 50, "budget": "2000.00", "csrfmiddlewaretoken": csrf_token},
        HTTP_ORIGIN="http://localhost:8080",
    )

    assert response.status_code == 302

"""Infrastructure-level smoke scenario: the start page can be requested.

This does not describe or implement Event-in-a-Box business behaviour. Needs
`django_db` as of specs/002-mvp-event-configuration-and-filtering: the start
page's Anlassart/preference fields now query the database when rendered.
"""

import pytest
from pytest_bdd import given, scenarios, then, when

scenarios("../features/stack_smoke.feature")

pytestmark = [pytest.mark.acceptance, pytest.mark.django_db]


@given("the Event in a Box application is running", target_fixture="app_client")
def app_client(client):
    return client


@when("I request the start page", target_fixture="start_page_response")
def start_page_response(app_client):
    return app_client.get("/")


@then("I receive a successful response")
def assert_successful_response(start_page_response):
    assert start_page_response.status_code == 200

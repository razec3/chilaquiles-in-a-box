"""Integration tests for the Working Skeleton view/session flow, exercising
spec.md's acceptance scenarios end-to-end through the real Django test
client and PostgreSQL-backed session store.

The former "no recipe satisfies the budget constraint" test (WS Scenario 8)
was removed here: specs/002-mvp-event-configuration-and-filtering (issue #8)
supersedes the 70%-of-budget suggestion cap outright, so that behavior no
longer exists. Equivalent "no matching recipe" coverage now lives in
tests/integration/test_event_configuration_and_filtering_views.py, driven by
Anlassart/preference classification instead of budget."""

import json

import pytest
from django.urls import reverse

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

RECIPE_ID = "zuercher-geschnetzeltes"


def _submit_event_input(client, guest_count=50, budget="2000.00"):
    return client.post(
        reverse("event_in_a_box:event_input"),
        {"guest_count": guest_count, "budget": budget},
    )


def test_happy_path_end_to_end(client):
    # Scenario 1: generate proposals within the 70% cap.
    response = _submit_event_input(client)
    assert response.status_code == 302
    assert response.url == reverse("event_in_a_box:suggestions")

    response = client.get(reverse("event_in_a_box:suggestions"))
    assert response.status_code == 200
    suggestions = response.context["suggestions"]
    assert len(suggestions) >= 1

    # Scenario 2: select and view a recipe with scaled ingredients.
    response = client.post(reverse("event_in_a_box:select_recipe", kwargs={"recipe_id": RECIPE_ID}))
    assert response.status_code == 302
    assert response.url == reverse("event_in_a_box:recipe_detail", kwargs={"recipe_id": RECIPE_ID})

    response = client.get(reverse("event_in_a_box:recipe_detail", kwargs={"recipe_id": RECIPE_ID}))
    assert response.status_code == 200
    package = response.context["package"]
    assert package.recipes[0].id == RECIPE_ID
    # Kalbsgeschnetzeltes: 0.2 kg/guest * 50 guests = 10 kg.
    kalbsgeschnetzeltes = next(
        r for r in package.product_requirements if r.product.article_number == "TG-10001"
    )
    assert kalbsgeschnetzeltes.required_quantity == 10

    # Scenario 3: confirm the recipe and generate the order draft.
    response = client.post(
        reverse("event_in_a_box:confirm_recipe", kwargs={"recipe_id": RECIPE_ID})
    )
    assert response.status_code == 302
    assert response.url == reverse("event_in_a_box:order_review")

    response = client.get(reverse("event_in_a_box:order_review"))
    assert response.status_code == 200
    assert response.context["package"].total_purchase_cost == 1100
    assert response.context["purchase_limit"] == 1400

    response = client.post(reverse("event_in_a_box:confirm_order"))
    assert response.status_code == 302
    assert response.url == reverse("event_in_a_box:order_confirmation")

    response = client.get(reverse("event_in_a_box:order_confirmation"))
    assert response.status_code == 200

    # Scenario 5: download the JSON order draft, no price fields.
    response = client.get(reverse("event_in_a_box:download_order"))
    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"
    assert "attachment" in response["Content-Disposition"]
    payload = json.loads(response.content)
    assert payload["guestCount"] == 50
    assert all("price" not in key.lower() for line in payload["lines"] for key in line)


def test_event_input_form_disables_native_html5_validation(client):
    # Regression: the number inputs carry min/step attributes as UX hints,
    # which make browsers block submission client-side before Django's own
    # validation (and its message text) ever runs, unless the form opts out
    # via novalidate. Caught by a real-browser walkthrough, not the Django
    # test client (which bypasses browser-side validation entirely).
    response = client.get(reverse("event_in_a_box:event_input"))

    assert b'<form method="post" novalidate>' in response.content


def test_reject_invalid_budget_shows_validation_message(client):
    # Scenario 6.
    response = _submit_event_input(client, budget="0")

    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["form"].errors["budget"]
    assert b"Bitte geben Sie ein Budget gr" in response.content


def test_reject_invalid_guest_count_shows_validation_message(client):
    # Scenario 7.
    response = _submit_event_input(client, guest_count=0)

    assert response.status_code == 200
    assert response.context["form"].errors["guest_count"]


def test_suggestions_without_planning_request_redirects_to_event_input(client):
    response = client.get(reverse("event_in_a_box:suggestions"))

    assert response.status_code == 302
    assert response.url == reverse("event_in_a_box:event_input")


def test_download_before_confirmation_redirects_to_event_input(client):
    _submit_event_input(client)
    client.post(reverse("event_in_a_box:select_recipe", kwargs={"recipe_id": RECIPE_ID}))

    response = client.get(reverse("event_in_a_box:download_order"))

    assert response.status_code == 302
    assert response.url == reverse("event_in_a_box:event_input")

"""Integration tests for the extended EventInputForm and the DB-backed
recipe classification filter (spec.md §7 —
Documentation/specs/002-mvp-event-configuration-and-filtering), exercised
through the real Django test client against the seeded reference/recipe data
(migrations 0002-0003)."""

import pytest
from django.urls import reverse

from event_in_a_box.models import Preference

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def _submit_event_input(
    client, guest_count=50, budget="2000.00", event_type_code="", preference_codes=()
):
    data = {"guest_count": guest_count, "budget": budget}
    if event_type_code:
        data["event_type"] = event_type_code
    if preference_codes:
        data["preferences"] = list(preference_codes)
    return client.post(reverse("event_in_a_box:event_input"), data)


def test_event_input_form_offers_the_seeded_event_type_and_preference_choices(client):
    response = client.get(reverse("event_in_a_box:event_input"))

    content = response.content.decode()
    assert "Business-Ap" in content
    assert "Vereinsanlass" in content
    assert "Brunch" in content
    assert "Vegetarisch" in content
    assert "Saisonal" in content


def test_event_input_rejects_more_than_four_preferences(client):
    # spec.md §4: "zero to four values" — enforced in EventInputForm, not
    # just by the UI (plan.md §4). Only 4 preferences are seeded, so an
    # extra one is created here to actually exceed the cap.
    Preference.objects.create(code="EXTRA", display_name="Extra", category="DIET")
    all_codes = list(Preference.objects.values_list("code", flat=True))
    assert len(all_codes) == 5

    response = _submit_event_input(client, preference_codes=all_codes)

    assert response.status_code == 200
    assert response.context["form"].errors["preferences"]


def test_suggestions_filters_by_event_type(client):
    # spec.md §7 Scenario 1.
    _submit_event_input(client, event_type_code="BUSINESS_APERO")

    response = client.get(reverse("event_in_a_box:suggestions"))

    names = {package.recipes[0].name for package in response.context["suggestions"]}
    assert names == {"Zürcher Geschnetzeltes mit Rösti"}


def test_suggestions_filters_by_preferences_with_and_semantics(client):
    # spec.md §7 Scenario 3.
    _submit_event_input(client, preference_codes=["VEGETARISCH", "SAISONAL"])

    response = client.get(reverse("event_in_a_box:suggestions"))

    names = {package.recipes[0].name for package in response.context["suggestions"]}
    assert names == {"Mediterraner Pasta-Abend"}


def test_suggestions_with_no_optional_filters_returns_all_recipes(client):
    # spec.md §7 Scenario 4.
    _submit_event_input(client)

    response = client.get(reverse("event_in_a_box:suggestions"))

    assert len(response.context["suggestions"]) == 3


def test_suggestions_shows_distinct_no_match_message_when_event_type_has_no_recipes(client):
    # spec.md §7 Scenario 5. BRUNCH is seeded with zero recipes (migrations/0002).
    _submit_event_input(client, event_type_code="BRUNCH")

    response = client.get(reverse("event_in_a_box:suggestions"))

    assert response.context["suggestions"] == []
    assert "kein passendes Rezept" in response.content.decode()


def test_changing_event_configuration_resets_previously_confirmed_recipe(client):
    # spec.md §7 Scenario 8.
    _submit_event_input(client)
    client.post(
        reverse("event_in_a_box:select_recipe", kwargs={"recipe_id": "zuercher-geschnetzeltes"})
    )
    client.post(
        reverse("event_in_a_box:confirm_recipe", kwargs={"recipe_id": "zuercher-geschnetzeltes"})
    )
    client.post(reverse("event_in_a_box:confirm_order"))

    _submit_event_input(client, guest_count=80)

    response = client.get(reverse("event_in_a_box:order_review"))
    assert response.status_code == 302
    assert response.url == reverse("event_in_a_box:event_input")

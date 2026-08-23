"""Step definitions for event_configuration_and_filtering.feature."""

from dataclasses import dataclass, field

import pytest
from django.test import Client
from django.urls import reverse
from pytest_bdd import given, parsers, scenarios, then, when

from event_in_a_box.models import EventType, Preference, Recipe

scenarios("../features/event_configuration_and_filtering.feature")

pytestmark = [pytest.mark.acceptance, pytest.mark.django_db]


@dataclass
class Flow:
    client: Client
    budget: str = "2000.00"
    guest_count: int = 50
    event_type_code: str = ""
    preference_codes: list = field(default_factory=list)
    response: object = field(default=None)


@pytest.fixture
def flow(client):
    return Flow(client=client)


def _submit_event_input(flow):
    data = {"guest_count": flow.guest_count, "budget": flow.budget}
    if flow.event_type_code:
        data["event_type"] = flow.event_type_code
    if flow.preference_codes:
        data["preferences"] = flow.preference_codes
    return flow.client.post(reverse("event_in_a_box:event_input"), data)


@given(parsers.parse('the budget is "{budget}" and the number of guests is {guest_count:d}'))
def set_budget_and_guests(flow, budget, guest_count):
    flow.budget = budget
    flow.guest_count = guest_count
    return flow


@given(parsers.parse('the Anlassart "{code}" is selected'))
def select_event_type(flow, code):
    flow.event_type_code = code
    return flow


@given(parsers.parse('the preference "{code}" is selected'))
def select_one_preference(flow, code):
    flow.preference_codes = [code]
    return flow


@given(parsers.parse('the preferences "{first}" and "{second}" are selected'))
def select_two_preferences(flow, first, second):
    flow.preference_codes = [first, second]
    return flow


@given(parsers.parse('the user has confirmed the recipe "{recipe_id}"'))
def has_confirmed_recipe(flow, recipe_id):
    _submit_event_input(flow)
    flow.client.post(reverse("event_in_a_box:select_recipe", kwargs={"recipe_id": recipe_id}))
    flow.client.post(reverse("event_in_a_box:confirm_recipe", kwargs={"recipe_id": recipe_id}))
    flow.client.post(reverse("event_in_a_box:confirm_order"))
    return flow


@when("the user requests recipe proposals")
def request_recipe_proposals(flow):
    _submit_event_input(flow)
    flow.response = flow.client.get(reverse("event_in_a_box:suggestions"))
    return flow


@when(
    parsers.parse(
        'the user requests recipe proposals with budget "{budget}" and {guest_count:d} guests'
    )
)
def request_recipe_proposals_with_input(flow, budget, guest_count):
    flow.budget = budget
    flow.guest_count = guest_count
    flow.response = _submit_event_input(flow)
    return flow


@when(parsers.parse("the user changes the number of guests to {guest_count:d}"))
def change_guest_count(flow, guest_count):
    flow.guest_count = guest_count
    flow.event_type_code = ""
    flow.preference_codes = []
    _submit_event_input(flow)
    flow.response = flow.client.get(reverse("event_in_a_box:order_review"))
    return flow


def _displayed_recipe_names(flow):
    return {package.recipes[0].name for package in flow.response.context["suggestions"]}


@then(parsers.parse('only recipes for the Anlassart "{code}" are displayed'))
def assert_only_recipes_for_event_type(flow, code):
    expected = set(EventType.objects.get(code=code).recipes.values_list("name", flat=True))
    assert expected, "fixture data must include at least one recipe for this Anlassart"
    assert _displayed_recipe_names(flow) == expected


@then(parsers.parse('only recipes with the preference "{code}" are displayed'))
def assert_only_recipes_with_preference(flow, code):
    expected = set(Preference.objects.get(code=code).recipes.values_list("name", flat=True))
    assert expected, "fixture data must include at least one recipe with this preference"
    assert _displayed_recipe_names(flow) == expected


@then(
    parsers.parse(
        'only recipes matching the Anlassart "{event_type_code}" and every selected '
        "preference are displayed"
    )
)
def assert_recipes_matching_event_type_and_preferences(flow, event_type_code):
    expected = set(
        Recipe.objects.filter(supported_event_types__code=event_type_code)
        .filter(preferences__code="VEGETARISCH")
        .filter(preferences__code="SAISONAL")
        .values_list("name", flat=True)
    )
    assert expected, "fixture data must include a recipe matching all active filters"
    assert _displayed_recipe_names(flow) == expected


@then("all available recipes are displayed")
def assert_all_recipes_displayed(flow):
    expected = set(Recipe.objects.values_list("name", flat=True))
    assert _displayed_recipe_names(flow) == expected


@then("the system informs the user that no matching recipe was found")
def assert_no_matching_recipe_message(flow):
    assert flow.response.status_code == 200
    assert flow.response.context["suggestions"] == []
    assert "kein passendes Rezept" in flow.response.content.decode()


@then("the user can return to the event configuration")
def assert_can_return_to_event_configuration(flow):
    assert reverse("event_in_a_box:event_input").encode() in flow.response.content


@then("the system blocks the request and shows a validation message")
def assert_blocked_with_validation_message(flow):
    assert flow.response.status_code == 200
    assert flow.response.context["form"].errors


@then("the previously confirmed recipe selection is discarded")
def assert_recipe_no_longer_confirmed(flow):
    assert flow.response.status_code == 302
    assert flow.response.url == reverse("event_in_a_box:event_input")

"""Step definitions for working_skeleton.feature."""

import json
from dataclasses import dataclass, field
from decimal import Decimal

import pytest
from django.test import Client
from django.urls import reverse
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../features/working_skeleton.feature")

pytestmark = [pytest.mark.acceptance, pytest.mark.django_db]


@dataclass
class Flow:
    client: Client
    budget: str = "0"
    guest_count: int = 0
    selected_recipe_id: str | None = None
    response: object = field(default=None)


@pytest.fixture
def flow(client):
    return Flow(client=client)


def _submit_event_input(flow):
    return flow.client.post(
        reverse("event_in_a_box:event_input"),
        {"guest_count": flow.guest_count, "budget": flow.budget},
    )


@given(parsers.parse('the budget is "{budget}" and the number of guests is {guest_count:d}'))
def set_budget_and_guests(flow, budget, guest_count):
    flow.budget = budget
    flow.guest_count = guest_count
    return flow


@given("the user has requested recipe proposals")
def has_requested_recipe_proposals(flow):
    _submit_event_input(flow)
    flow.response = flow.client.get(reverse("event_in_a_box:suggestions"))
    return flow


@given(parsers.parse('the user has selected the recipe "{recipe_id}"'))
def has_selected_recipe(flow, recipe_id):
    _submit_event_input(flow)
    flow.client.get(reverse("event_in_a_box:suggestions"))
    flow.client.post(reverse("event_in_a_box:select_recipe", kwargs={"recipe_id": recipe_id}))
    flow.selected_recipe_id = recipe_id
    flow.response = flow.client.get(
        reverse("event_in_a_box:recipe_detail", kwargs={"recipe_id": recipe_id})
    )
    return flow


@given(parsers.parse('the user has confirmed the recipe "{recipe_id}"'))
def has_confirmed_recipe(flow, recipe_id):
    _submit_event_input(flow)
    flow.client.post(reverse("event_in_a_box:select_recipe", kwargs={"recipe_id": recipe_id}))
    flow.client.post(reverse("event_in_a_box:confirm_recipe", kwargs={"recipe_id": recipe_id}))
    flow.client.post(reverse("event_in_a_box:confirm_order"))
    flow.selected_recipe_id = recipe_id
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


@when(parsers.parse('the user selects the recipe "{recipe_id}"'))
def select_recipe(flow, recipe_id):
    flow.client.post(reverse("event_in_a_box:select_recipe", kwargs={"recipe_id": recipe_id}))
    flow.selected_recipe_id = recipe_id
    flow.response = flow.client.get(
        reverse("event_in_a_box:recipe_detail", kwargs={"recipe_id": recipe_id})
    )
    return flow


@when("the user confirms the selected recipe")
def confirm_selected_recipe(flow):
    flow.client.post(
        reverse("event_in_a_box:confirm_recipe", kwargs={"recipe_id": flow.selected_recipe_id})
    )
    flow.response = flow.client.get(reverse("event_in_a_box:order_review"))
    return flow


@when("the user requests the JSON download")
def request_json_download(flow):
    flow.response = flow.client.get(reverse("event_in_a_box:download_order"))
    return flow


@then("the system displays one or more recipe proposals")
def assert_one_or_more_proposals(flow):
    assert flow.response.status_code == 200
    assert len(flow.response.context["suggestions"]) >= 1


@then(parsers.parse("every displayed recipe proposal has a total price of at most CHF {limit}"))
def assert_proposals_within_limit(flow, limit):
    for package in flow.response.context["suggestions"]:
        assert package.total_purchase_cost <= Decimal(limit)


@then("the system displays the selected recipe with its scaled ingredients")
def assert_selected_recipe_displayed(flow):
    assert flow.response.status_code == 200
    package = flow.response.context["package"]
    assert package.recipes[0].id == flow.selected_recipe_id
    assert len(package.product_requirements) > 0


@then("the system displays an order draft with product, packs, and total price")
def assert_order_draft_displayed(flow):
    assert flow.response.status_code == 200
    package = flow.response.context["package"]
    assert len(package.product_requirements) > 0
    for requirement in package.product_requirements:
        assert requirement.required_package_count > 0
    assert package.total_purchase_cost > 0


@then("the system downloads a JSON order draft without price information")
def assert_json_download_without_price(flow):
    assert flow.response.status_code == 200
    assert flow.response["Content-Type"] == "application/json"
    payload = json.loads(flow.response.content)
    assert all("price" not in key.lower() for line in payload["lines"] for key in line)


@then("the system blocks the request and shows a validation message")
def assert_blocked_with_validation_message(flow):
    assert flow.response.status_code == 200
    assert flow.response.context["form"].errors


@then("the system informs the user that no suitable recipe can be proposed")
def assert_no_suitable_recipe_message(flow):
    assert flow.response.status_code == 200
    assert flow.response.context["suggestions"] == []
    assert "kein passendes Menü" in flow.response.content.decode()

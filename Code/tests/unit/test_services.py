"""Unit tests for find_recipe_suggestions (spec.md §7 Scenarios 1, 4, 5 —
specs/002-mvp-event-configuration-and-filtering) and the order-review-only
purchase_limit helper (specs/001-working-skeleton)."""

from decimal import Decimal

import pytest

from event_in_a_box.domain import (
    AperoPackageCalculator,
    EventType,
    Ingredient,
    MeasurementUnit,
    PackageType,
    PlanningRequest,
    Preference,
    PreferenceCategory,
    Product,
    Recipe,
)
from event_in_a_box.services import find_recipe_suggestions, purchase_limit

pytestmark = pytest.mark.unit

BUSINESS_APERO = EventType(code="BUSINESS_APERO", display_name="Business-Apéro")
VEREINSANLASS = EventType(code="VEREINSANLASS", display_name="Vereinsanlass")
VEGETARISCH = Preference(
    code="VEGETARISCH", display_name="Vegetarisch", category=PreferenceCategory.DIET
)


def _recipe(recipe_id, price="10.00", event_types=(), preferences=()):
    product = Product(
        article_number=recipe_id,
        name=recipe_id,
        package_quantity=Decimal("1"),
        measured_in=MeasurementUnit.PIECE,
        sold_in=PackageType.PIECE,
        purchase_price_per_package=Decimal(price),
    )
    return Recipe(
        id=recipe_id,
        name=recipe_id,
        description="",
        ingredients=(Ingredient(product=product, quantity_per_guest=Decimal("1")),),
        supported_event_types=event_types,
        preferences=preferences,
    )


def test_purchase_limit_is_seventy_percent_of_budget():
    # specs/001-working-skeleton's order-review display only; no longer used
    # to filter suggestions as of 002 (issue #8).
    assert purchase_limit(Decimal("2000")) == Decimal("1400.00")


def test_all_recipes_are_suggested_when_no_filters_are_active():
    # spec.md §7 Scenario 4. Budget no longer filters eligibility (spec.md
    # §6): "expensive" is suggested even though it far exceeds the budget.
    cheap_recipe = _recipe("cheap", price="10.00")
    expensive_recipe = _recipe("expensive", price="1000.00")
    request = PlanningRequest(guest_count=1, maximum_budget=Decimal("1"))

    suggestions = find_recipe_suggestions(
        [cheap_recipe, expensive_recipe], request, AperoPackageCalculator()
    )

    assert {package.recipes[0].id for package in suggestions} == {"cheap", "expensive"}


def test_only_recipes_matching_the_selected_event_type_are_suggested():
    # spec.md §7 Scenario 1.
    matching_recipe = _recipe("matching", event_types=(BUSINESS_APERO,))
    other_recipe = _recipe("other", event_types=(VEREINSANLASS,))
    request = PlanningRequest(
        guest_count=1, maximum_budget=Decimal("1000"), event_type=BUSINESS_APERO
    )

    suggestions = find_recipe_suggestions(
        [matching_recipe, other_recipe], request, AperoPackageCalculator()
    )

    assert [package.recipes[0].id for package in suggestions] == ["matching"]


def test_no_recipe_matches_the_active_filters():
    # spec.md §7 Scenario 5.
    recipe = _recipe("r1", event_types=(VEREINSANLASS,))
    request = PlanningRequest(
        guest_count=1, maximum_budget=Decimal("1000"), event_type=BUSINESS_APERO
    )

    suggestions = find_recipe_suggestions([recipe], request, AperoPackageCalculator())

    assert suggestions == []


def test_recipe_missing_a_selected_preference_is_excluded():
    # spec.md §7 Scenario 2.
    recipe = _recipe("r1", preferences=())
    request = PlanningRequest(
        guest_count=1, maximum_budget=Decimal("1000"), selected_preferences=(VEGETARISCH,)
    )

    suggestions = find_recipe_suggestions([recipe], request, AperoPackageCalculator())

    assert suggestions == []

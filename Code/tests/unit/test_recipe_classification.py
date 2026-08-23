"""Unit tests for Recipe.matches_classification (spec.md §6-7, 002 —
Documentation/specs/002-mvp-event-configuration-and-filtering). Pure Python:
no Django, no PostgreSQL."""

from decimal import Decimal

import pytest

from event_in_a_box.domain import (
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

pytestmark = pytest.mark.unit

BUSINESS_APERO = EventType(code="BUSINESS_APERO", display_name="Business-Apéro")
VEREINSANLASS = EventType(code="VEREINSANLASS", display_name="Vereinsanlass")
VEGETARISCH = Preference(
    code="VEGETARISCH", display_name="Vegetarisch", category=PreferenceCategory.DIET
)
SAISONAL = Preference(
    code="SAISONAL", display_name="Saisonal", category=PreferenceCategory.SEASONALITY
)


def _recipe(event_types=(), preferences=()):
    product = Product(
        article_number="P1",
        name="P1",
        package_quantity=Decimal("1"),
        measured_in=MeasurementUnit.PIECE,
        sold_in=PackageType.PIECE,
        purchase_price_per_package=Decimal("1.00"),
    )
    return Recipe(
        id="r1",
        name="Recipe",
        description="",
        ingredients=(Ingredient(product=product, quantity_per_guest=Decimal("1")),),
        supported_event_types=event_types,
        preferences=preferences,
    )


def _request(event_type=None, preferences=()):
    return PlanningRequest(
        guest_count=1,
        maximum_budget=Decimal("1000"),
        event_type=event_type,
        selected_preferences=preferences,
    )


def test_no_filters_active_the_recipe_is_eligible():
    # spec.md §7 Scenario 4.
    recipe = _recipe(event_types=(BUSINESS_APERO,), preferences=(VEGETARISCH,))

    assert recipe.matches_classification(_request()) is True


def test_recipe_supporting_the_selected_event_type_is_eligible():
    # spec.md §7 Scenario 1.
    recipe = _recipe(event_types=(BUSINESS_APERO,))

    assert recipe.matches_classification(_request(event_type=BUSINESS_APERO)) is True


def test_recipe_not_supporting_the_selected_event_type_is_excluded():
    # spec.md §7 Scenario 1.
    recipe = _recipe(event_types=(VEREINSANLASS,))

    assert recipe.matches_classification(_request(event_type=BUSINESS_APERO)) is False


def test_recipe_carrying_the_single_selected_preference_is_eligible():
    # spec.md §7 Scenario 2.
    recipe = _recipe(preferences=(VEGETARISCH,))

    assert recipe.matches_classification(_request(preferences=(VEGETARISCH,))) is True


def test_recipe_missing_the_single_selected_preference_is_excluded():
    # spec.md §7 Scenario 2.
    recipe = _recipe(preferences=(SAISONAL,))

    assert recipe.matches_classification(_request(preferences=(VEGETARISCH,))) is False


def test_recipe_matching_event_type_and_every_selected_preference_is_eligible():
    # spec.md §7 Scenario 3 (AND semantics across Anlassart + preferences).
    recipe = _recipe(event_types=(BUSINESS_APERO,), preferences=(VEGETARISCH, SAISONAL))
    request = _request(event_type=BUSINESS_APERO, preferences=(VEGETARISCH, SAISONAL))

    assert recipe.matches_classification(request) is True


def test_recipe_missing_one_of_several_selected_preferences_is_excluded():
    # spec.md §7 Scenario 3: a recipe must satisfy every active filter.
    recipe = _recipe(event_types=(BUSINESS_APERO,), preferences=(VEGETARISCH,))
    request = _request(event_type=BUSINESS_APERO, preferences=(VEGETARISCH, SAISONAL))

    assert recipe.matches_classification(request) is False

"""Unit tests for the Working-Skeleton-specific 70%-of-budget suggestion
filter (spec.md Scenarios 1 and 8)."""

from decimal import Decimal

import pytest

from event_in_a_box.domain import (
    AperoPackageCalculator,
    Ingredient,
    MeasurementUnit,
    PackageType,
    PlanningRequest,
    Product,
    Recipe,
)
from event_in_a_box.services import find_recipe_suggestions, purchase_limit

pytestmark = pytest.mark.unit


def _recipe(recipe_id, price):
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
    )


def test_purchase_limit_is_seventy_percent_of_budget():
    assert purchase_limit(Decimal("2000")) == Decimal("1400.00")


def test_recipes_within_the_purchase_limit_are_suggested():
    cheap_recipe = _recipe("cheap", "10.00")
    expensive_recipe = _recipe("expensive", "1000.00")
    request = PlanningRequest(guest_count=1, maximum_budget=Decimal("100"))

    suggestions = find_recipe_suggestions(
        [cheap_recipe, expensive_recipe], request, AperoPackageCalculator()
    )

    assert [package.recipes[0].id for package in suggestions] == ["cheap"]


def test_no_recipe_satisfies_the_budget_constraint():
    # spec.md Scenario 8.
    expensive_recipe = _recipe("expensive", "1000.00")
    request = PlanningRequest(guest_count=1, maximum_budget=Decimal("100"))

    suggestions = find_recipe_suggestions([expensive_recipe], request, AperoPackageCalculator())

    assert suggestions == []


def test_recipe_exactly_at_the_purchase_limit_is_suggested():
    # 70% of 100 = 70.00, boundary case ("less than or equal to").
    boundary_recipe = _recipe("boundary", "70.00")
    request = PlanningRequest(guest_count=1, maximum_budget=Decimal("100"))

    suggestions = find_recipe_suggestions([boundary_recipe], request, AperoPackageCalculator())

    assert len(suggestions) == 1

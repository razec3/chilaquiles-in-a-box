"""Unit tests for AperoPackageCalculator (spec.md Scenario 4 and CLAUDE.md
business rules 16-20). Pure Python: no Django, no PostgreSQL."""

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

pytestmark = pytest.mark.unit


def _product(article_number, package_quantity, price, measured_in=MeasurementUnit.KILOGRAM):
    return Product(
        article_number=article_number,
        name=article_number,
        package_quantity=Decimal(package_quantity),
        measured_in=measured_in,
        sold_in=PackageType.BAG,
        purchase_price_per_package=Decimal(price),
    )


def test_pack_rounding_rounds_up_to_the_next_whole_package():
    # spec.md Scenario 4: 1.2 kg required, 1 kg packs -> 2 packs.
    product = _product("P1", "1", "10.00")
    recipe = Recipe(
        id="r1",
        name="Recipe",
        description="",
        ingredients=(Ingredient(product=product, quantity_per_guest=Decimal("0.12")),),
    )
    request = PlanningRequest(guest_count=10, maximum_budget=Decimal("1000"))

    package = AperoPackageCalculator().calculate([recipe], request)

    (requirement,) = package.product_requirements
    assert requirement.required_quantity == Decimal("1.2")
    assert requirement.required_package_count == 2
    assert requirement.line_cost == Decimal("20.00")


def test_ingredient_quantities_scale_linearly_with_guest_count():
    product = _product("P1", "100", "5.00")
    recipe = Recipe(
        id="r1",
        name="Recipe",
        description="",
        ingredients=(Ingredient(product=product, quantity_per_guest=Decimal("2")),),
    )
    request = PlanningRequest(guest_count=25, maximum_budget=Decimal("1000"))

    package = AperoPackageCalculator().calculate([recipe], request)

    (requirement,) = package.product_requirements
    assert requirement.required_quantity == Decimal("50")


def test_shared_products_are_aggregated_before_package_rounding():
    shared_product = _product("SHARED", "10", "3.00")
    recipe_a = Recipe(
        id="a",
        name="A",
        description="",
        ingredients=(Ingredient(product=shared_product, quantity_per_guest=Decimal("0.3")),),
    )
    recipe_b = Recipe(
        id="b",
        name="B",
        description="",
        ingredients=(Ingredient(product=shared_product, quantity_per_guest=Decimal("0.4")),),
    )
    request = PlanningRequest(guest_count=10, maximum_budget=Decimal("1000"))

    # Aggregated: (0.3 + 0.4) * 10 = 7 required -> ceil(7/10) = 1 pack.
    # If rounded per recipe instead: ceil(3/10) + ceil(4/10) = 1 + 1 = 2 packs.
    # The lower, aggregated result proves quantities are summed before rounding.
    package = AperoPackageCalculator().calculate([recipe_a, recipe_b], request)

    (requirement,) = package.product_requirements
    assert requirement.required_quantity == Decimal("7.0")
    assert requirement.required_package_count == 1


def test_total_cost_and_cost_per_guest():
    product_one = _product("P1", "1", "10.00")
    product_two = _product("P2", "1", "6.00")
    recipe = Recipe(
        id="r1",
        name="Recipe",
        description="",
        ingredients=(
            Ingredient(product=product_one, quantity_per_guest=Decimal("1")),
            Ingredient(product=product_two, quantity_per_guest=Decimal("1")),
        ),
    )
    request = PlanningRequest(guest_count=4, maximum_budget=Decimal("1000"))

    package = AperoPackageCalculator().calculate([recipe], request)

    assert package.total_purchase_cost == Decimal("64.00")
    assert package.purchase_cost_per_guest == Decimal("16.00")


def test_calculate_requires_at_least_one_recipe():
    request = PlanningRequest(guest_count=4, maximum_budget=Decimal("1000"))

    with pytest.raises(ValueError):
        AperoPackageCalculator().calculate([], request)

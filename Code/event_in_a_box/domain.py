"""Canonical domain model subset used by the Working Skeleton.

Framework-free: no Django, HTTP, JSON, or database imports. See
Documentation/specs/001-working-skeleton/data-model.md for which parts of the
project-wide domain model (Documentation/Architecture/event-in-a-box-domain-model-and-erm.md)
this covers, and plan.md §6 for the one deliberate deviation (no BudgetStatus /
over-budget confirmation in the Working Skeleton).
"""

import math
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from enum import Enum

TWO_PLACES = Decimal("0.01")


def round_money(value: Decimal) -> Decimal:
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


class MeasurementUnit(Enum):
    PIECE = "PIECE"
    GRAM = "GRAM"
    KILOGRAM = "KILOGRAM"
    MILLILITRE = "MILLILITRE"
    LITRE = "LITRE"


class PackageType(Enum):
    TUBE = "TUBE"
    BOTTLE = "BOTTLE"
    BAG = "BAG"
    BOX = "BOX"
    CAN = "CAN"
    PACKAGE = "PACKAGE"
    PIECE = "PIECE"


@dataclass(frozen=True)
class Product:
    article_number: str
    name: str
    package_quantity: Decimal
    measured_in: MeasurementUnit
    sold_in: PackageType
    purchase_price_per_package: Decimal


@dataclass(frozen=True)
class Ingredient:
    product: Product
    quantity_per_guest: Decimal


class PreferenceCategory(Enum):
    DIET = "DIET"
    ORIGIN = "ORIGIN"
    SEASONALITY = "SEASONALITY"
    CERTIFICATION = "CERTIFICATION"


@dataclass(frozen=True)
class EventType:
    """Anlassart (spec.md §4)."""

    code: str
    display_name: str


@dataclass(frozen=True)
class Preference:
    """Persönliche Präferenz (spec.md §4)."""

    code: str
    display_name: str
    category: PreferenceCategory


@dataclass(frozen=True)
class Recipe:
    id: str
    name: str
    description: str
    ingredients: tuple[Ingredient, ...]
    supported_event_types: tuple[EventType, ...] = ()
    preferences: tuple[Preference, ...] = ()

    def matches_classification(self, request: "PlanningRequest") -> bool:
        """spec.md §6-7 (002): Anlassart and every selected preference are

        hard (AND) filters; unset filters do not restrict eligibility.
        """
        event_type_matches = request.event_type is None or any(
            event_type.code == request.event_type.code
            for event_type in self.supported_event_types
        )
        preferences_match = all(
            any(preference.code == candidate.code for candidate in self.preferences)
            for preference in request.selected_preferences
        )
        return event_type_matches and preferences_match


@dataclass(frozen=True)
class PlanningRequest:
    guest_count: int
    maximum_budget: Decimal
    event_type: EventType | None = None
    selected_preferences: tuple[Preference, ...] = ()


@dataclass(frozen=True)
class ProductRequirement:
    product: Product
    required_quantity: Decimal
    required_package_count: int
    line_cost: Decimal


@dataclass(frozen=True)
class AperoPackage:
    recipes: tuple[Recipe, ...]
    product_requirements: tuple[ProductRequirement, ...]
    total_purchase_cost: Decimal
    purchase_cost_per_guest: Decimal
    maximum_budget: Decimal


class AperoPackageCalculator:
    """The single calculation algorithm for one or more recipes.

    CLAUDE.md business rules 16-20: shared products are aggregated before
    package rounding; package count is ceil(required / package quantity);
    line cost and totals follow from that.
    """

    def calculate(self, recipes: list[Recipe], request: PlanningRequest) -> AperoPackage:
        if not recipes:
            raise ValueError("At least one recipe must be selected.")

        quantities: dict[str, Decimal] = {}
        products: dict[str, Product] = {}
        for recipe in recipes:
            for ingredient in recipe.ingredients:
                article_number = ingredient.product.article_number
                products[article_number] = ingredient.product
                required = ingredient.quantity_per_guest * request.guest_count
                quantities[article_number] = quantities.get(article_number, Decimal(0)) + required

        requirements = []
        total_cost = Decimal(0)
        for article_number, required_quantity in quantities.items():
            product = products[article_number]
            package_count = math.ceil(required_quantity / product.package_quantity)
            line_cost = round_money(Decimal(package_count) * product.purchase_price_per_package)
            requirements.append(
                ProductRequirement(
                    product=product,
                    required_quantity=required_quantity,
                    required_package_count=package_count,
                    line_cost=line_cost,
                )
            )
            total_cost += line_cost

        total_cost = round_money(total_cost)
        cost_per_guest = round_money(total_cost / request.guest_count)

        return AperoPackage(
            recipes=tuple(recipes),
            product_requirements=tuple(requirements),
            total_purchase_cost=total_cost,
            purchase_cost_per_guest=cost_per_guest,
            maximum_budget=request.maximum_budget,
        )

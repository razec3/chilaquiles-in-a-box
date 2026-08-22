"""Application/domain-logic layer for the Working Skeleton.

Holds the Working-Skeleton-specific 70%-of-budget suggestion filter (see
Documentation/specs/001-working-skeleton/plan.md §6 for why this is not part
of the canonical AperoPackageCalculator) and the session-backed flow state
that carries the planning request and selection between page requests.
"""

from decimal import Decimal

from django.http import HttpRequest

from .domain import AperoPackage, AperoPackageCalculator, PlanningRequest, Recipe, round_money

PURCHASE_LIMIT_RATIO = Decimal("0.70")

_SESSION_GUEST_COUNT = "working_skeleton_guest_count"
_SESSION_BUDGET = "working_skeleton_budget"
_SESSION_SELECTED_RECIPE_ID = "working_skeleton_selected_recipe_id"
_SESSION_ORDER_CONFIRMED = "working_skeleton_order_confirmed"


def purchase_limit(maximum_budget: Decimal) -> Decimal:
    """The Working Skeleton's suggestion-eligibility ceiling: 70% of budget."""
    return round_money(maximum_budget * PURCHASE_LIMIT_RATIO)


def find_recipe_suggestions(
    recipes: list[Recipe], request: PlanningRequest, calculator: AperoPackageCalculator
) -> list[AperoPackage]:
    """Recipes whose calculated total stays within 70% of the budget.

    spec.md Scenario 1/8. Each recipe is evaluated on its own (the Working
    Skeleton only ever selects one recipe), reusing the same
    AperoPackageCalculator.calculate() used for the final order draft.
    """
    limit = purchase_limit(request.maximum_budget)
    suggestions = []
    for recipe in recipes:
        package = calculator.calculate([recipe], request)
        if package.total_purchase_cost <= limit:
            suggestions.append(package)
    return suggestions


class PlanningSession:
    """Thin wrapper around the Django session for the Working Skeleton flow.

    Only the three primitive inputs (guest count, budget, selected recipe id)
    and a confirmation flag are stored; every page recomputes the
    AperoPackage from these via the repositories and calculator, so nothing
    here needs to serialize domain objects.
    """

    def __init__(self, request: HttpRequest):
        self._session = request.session

    @property
    def guest_count(self) -> int | None:
        return self._session.get(_SESSION_GUEST_COUNT)

    @property
    def maximum_budget(self) -> Decimal | None:
        value = self._session.get(_SESSION_BUDGET)
        return Decimal(value) if value is not None else None

    @property
    def selected_recipe_id(self) -> str | None:
        return self._session.get(_SESSION_SELECTED_RECIPE_ID)

    @property
    def order_confirmed(self) -> bool:
        return bool(self._session.get(_SESSION_ORDER_CONFIRMED, False))

    @property
    def has_planning_request(self) -> bool:
        return self.guest_count is not None and self.maximum_budget is not None

    def to_planning_request(self) -> PlanningRequest | None:
        if not self.has_planning_request:
            return None
        return PlanningRequest(guest_count=self.guest_count, maximum_budget=self.maximum_budget)

    def start(self, guest_count: int, maximum_budget: Decimal) -> None:
        self._session[_SESSION_GUEST_COUNT] = guest_count
        self._session[_SESSION_BUDGET] = str(maximum_budget)
        self._session[_SESSION_SELECTED_RECIPE_ID] = None
        self._session[_SESSION_ORDER_CONFIRMED] = False

    def select_recipe(self, recipe_id: str) -> None:
        self._session[_SESSION_SELECTED_RECIPE_ID] = recipe_id
        self._session[_SESSION_ORDER_CONFIRMED] = False

    def confirm_order(self) -> None:
        self._session[_SESSION_ORDER_CONFIRMED] = True

    def clear(self) -> None:
        for key in (
            _SESSION_GUEST_COUNT,
            _SESSION_BUDGET,
            _SESSION_SELECTED_RECIPE_ID,
            _SESSION_ORDER_CONFIRMED,
        ):
            self._session.pop(key, None)

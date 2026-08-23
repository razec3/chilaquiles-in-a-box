"""Application/domain-logic layer.

Holds the session-backed flow state that carries the planning request and
selection between page requests, plus the recipe-suggestion query. `purchase_limit`
is a Working-Skeleton-era helper (Documentation/specs/001-working-skeleton/plan.md §6)
kept only for the order-review screen's own display; as of `002` it no longer
gates recipe suggestions (spec.md §2, issue #8) — `find_recipe_suggestions` now
filters purely via `Recipe.matches_classification`.
"""

from decimal import Decimal

from django.http import HttpRequest

from .domain import AperoPackage, AperoPackageCalculator, PlanningRequest, Recipe, round_money
from .repositories import DatabaseEventTypeRepository, DatabasePreferenceRepository

PURCHASE_LIMIT_RATIO = Decimal("0.70")

_SESSION_GUEST_COUNT = "working_skeleton_guest_count"
_SESSION_BUDGET = "working_skeleton_budget"
_SESSION_EVENT_TYPE_CODE = "planning_event_type_code"
_SESSION_PREFERENCE_CODES = "planning_preference_codes"
_SESSION_SELECTED_RECIPE_ID = "working_skeleton_selected_recipe_id"
_SESSION_ORDER_CONFIRMED = "working_skeleton_order_confirmed"

_event_type_repository = DatabaseEventTypeRepository()
_preference_repository = DatabasePreferenceRepository()


def purchase_limit(maximum_budget: Decimal) -> Decimal:
    """The Working Skeleton order-review screen's display ceiling: 70% of budget."""
    return round_money(maximum_budget * PURCHASE_LIMIT_RATIO)


def find_recipe_suggestions(
    recipes: list[Recipe], request: PlanningRequest, calculator: AperoPackageCalculator
) -> list[AperoPackage]:
    """Recipes matching the request's Anlassart/preferences classification.

    spec.md §6-7 (002): every selected preference and, when specified,
    Anlassart are hard filters; budget does not filter eligibility. Each
    matching recipe is evaluated on its own, reusing the same
    AperoPackageCalculator.calculate() used for the final order draft.
    """
    return [
        calculator.calculate([recipe], request)
        for recipe in recipes
        if recipe.matches_classification(request)
    ]


class PlanningSession:
    """Thin wrapper around the Django session for the planning flow.

    Only primitive inputs (guest count, budget, event-type/preference codes,
    selected recipe id) and a confirmation flag are stored; every page
    recomputes the AperoPackage from these via the repositories and
    calculator, so nothing here needs to serialize domain objects.
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
    def event_type_code(self) -> str | None:
        return self._session.get(_SESSION_EVENT_TYPE_CODE)

    @property
    def preference_codes(self) -> tuple[str, ...]:
        return tuple(self._session.get(_SESSION_PREFERENCE_CODES, ()))

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
        event_type = (
            _event_type_repository.get_by_code(self.event_type_code)
            if self.event_type_code
            else None
        )
        preferences = _preference_repository.get_by_codes(self.preference_codes)
        return PlanningRequest(
            guest_count=self.guest_count,
            maximum_budget=self.maximum_budget,
            event_type=event_type,
            selected_preferences=preferences,
        )

    def start(
        self,
        guest_count: int,
        maximum_budget: Decimal,
        event_type_code: str | None = None,
        preference_codes: tuple[str, ...] = (),
    ) -> None:
        """Starts (or restarts) the planning flow.

        spec.md §7 Scenario 8: changing any event input resets all
        downstream state, so this unconditionally clears the selection and
        confirmation flag even when called again for an already-started flow.
        """
        self._session[_SESSION_GUEST_COUNT] = guest_count
        self._session[_SESSION_BUDGET] = str(maximum_budget)
        self._session[_SESSION_EVENT_TYPE_CODE] = event_type_code
        self._session[_SESSION_PREFERENCE_CODES] = list(preference_codes)
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
            _SESSION_EVENT_TYPE_CODE,
            _SESSION_PREFERENCE_CODES,
            _SESSION_SELECTED_RECIPE_ID,
            _SESSION_ORDER_CONFIRMED,
        ):
            self._session.pop(key, None)

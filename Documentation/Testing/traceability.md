# Testing Traceability

Maps requirements — `CLAUDE.md` business rules and feature `spec.md` acceptance criteria — to the
automated tests that verify them, per `CLAUDE.md`'s testing strategy. Business rule text itself
lives in `CLAUDE.md` or the relevant `spec.md`; this file only cross-references, it does not repeat
that text.

All test paths are relative to `Code/`. Run `docker compose run --rm web pytest` for the full
suite, or `pytest tests/<unit|integration|acceptance>` for one category.

## Technical foundation

| Requirement | Test |
|---|---|
| `/health/` returns a deterministic 200 JSON payload | `tests/unit/test_health_view.py::test_health_endpoint_returns_deterministic_ok_payload` |
| Django can connect to PostgreSQL | `tests/integration/test_database_connection.py::test_django_can_connect_to_postgresql` |
| The configured application loads successfully | `tests/integration/test_application_stack.py::test_start_page_loads_successfully` |
| The app is reachable through the nginx entry point (CSRF trusted origin) | `tests/integration/test_application_stack.py::test_post_requests_through_the_nginx_origin_are_not_blocked_by_csrf` |
| The start page can be requested (stack smoke test) | `tests/acceptance/features/stack_smoke.feature` → `Scenario: Request the application start page` |

## Feature: `specs/001-working-skeleton`

Requirements are `spec.md`'s numbered acceptance scenarios (§7). See
`specs/001-working-skeleton/plan.md` §8 for which test *level* each scenario was assigned to and
why; this table is the resulting concrete mapping.

| `spec.md` scenario | Unit | Integration | Acceptance |
|---|---|---|---|
| 1 — Generate recipe proposals with valid input | `tests/unit/test_services.py::test_recipes_within_the_purchase_limit_are_suggested`, `::test_purchase_limit_is_seventy_percent_of_budget`, `::test_recipe_exactly_at_the_purchase_limit_is_suggested` | `tests/integration/test_working_skeleton_views.py::test_happy_path_end_to_end` | `working_skeleton.feature` → `Scenario: Generate recipe proposals with valid input` |
| 2 — View a selected recipe | — | `test_working_skeleton_views.py::test_happy_path_end_to_end` | `working_skeleton.feature` → `Scenario: View a selected recipe` |
| 3 — Confirm a recipe and generate an order draft | — | `test_working_skeleton_views.py::test_happy_path_end_to_end` | `working_skeleton.feature` → `Scenario: Confirm a recipe and generate an order draft` |
| 4 — Calculate required packing units | `tests/unit/test_domain.py::test_pack_rounding_rounds_up_to_the_next_whole_package` | — | — |
| 5 — Download the order draft | `tests/unit/test_exporters.py::test_export_contains_no_price_fields`, `::test_export_contains_expected_values`, `::test_export_document_metadata` | `test_working_skeleton_views.py::test_happy_path_end_to_end`, `::test_download_before_confirmation_redirects_to_event_input` | `working_skeleton.feature` → `Scenario: Download the order draft` |
| 6 — Reject invalid budget | — | `test_working_skeleton_views.py::test_reject_invalid_budget_shows_validation_message`, `::test_event_input_form_disables_native_html5_validation` | `working_skeleton.feature` → `Scenario: Reject invalid budget` |
| 7 — Reject invalid number of guests | — | `test_working_skeleton_views.py::test_reject_invalid_guest_count_shows_validation_message` | `working_skeleton.feature` → `Scenario: Reject invalid number of guests` |
| 8 — No recipe satisfies the budget constraint | `tests/unit/test_services.py::test_no_recipe_satisfies_the_budget_constraint` | `test_working_skeleton_views.py::test_no_recipe_satisfies_the_budget_constraint` | `working_skeleton.feature` → `Scenario: No recipe satisfies the budget constraint` |

Not tied to one numbered scenario, but exercised throughout:

| Requirement | Test |
|---|---|
| Ingredient quantities scale linearly with guest count | `tests/unit/test_domain.py::test_ingredient_quantities_scale_linearly_with_guest_count` |
| Shared products are aggregated before package rounding | `tests/unit/test_domain.py::test_shared_products_are_aggregated_before_package_rounding` |
| Total cost and cost-per-guest calculation | `tests/unit/test_domain.py::test_total_cost_and_cost_per_guest` |
| `AperoPackageCalculator.calculate` requires at least one recipe | `tests/unit/test_domain.py::test_calculate_requires_at_least_one_recipe` |
| A page without the required session state redirects to the event input | `test_working_skeleton_views.py::test_suggestions_without_planning_request_redirects_to_event_input` |

**Superseded by `specs/002-mvp-event-configuration-and-filtering` (issue #8):** the Working
Skeleton's own Scenario 8 ("no recipe satisfies the budget constraint" — a 70%-of-budget suggestion
cap) no longer describes real system behavior and was removed from
`tests/acceptance/features/working_skeleton.feature`, `tests/acceptance/step_definitions/test_working_skeleton.py`,
`tests/integration/test_working_skeleton_views.py`, and `tests/unit/test_services.py`. Its
replacement — a "no matching recipe" result driven by Anlassart/preference classification instead
of budget — is covered by `002`'s own Scenario 5 below.

## Feature: `specs/002-mvp-event-configuration-and-filtering`

Requirements are `spec.md`'s numbered acceptance scenarios (§7).

| `spec.md` scenario | Unit | Integration | Acceptance |
|---|---|---|---|
| 1 — Filter by Anlassart | `tests/unit/test_recipe_classification.py::test_recipe_supporting_the_selected_event_type_is_eligible`, `::test_recipe_not_supporting_the_selected_event_type_is_excluded`; `tests/unit/test_services.py::test_only_recipes_matching_the_selected_event_type_are_suggested` | `tests/integration/test_event_configuration_and_filtering_views.py::test_suggestions_filters_by_event_type` | `event_configuration_and_filtering.feature` → `Scenario: Filter by Anlassart` |
| 2 — Filter by one preference | `tests/unit/test_recipe_classification.py::test_recipe_carrying_the_single_selected_preference_is_eligible`, `::test_recipe_missing_the_single_selected_preference_is_excluded`; `tests/unit/test_services.py::test_recipe_missing_a_selected_preference_is_excluded` | — | `event_configuration_and_filtering.feature` → `Scenario: Filter by one preference` |
| 3 — Combine Anlassart and multiple preferences | `tests/unit/test_recipe_classification.py::test_recipe_matching_event_type_and_every_selected_preference_is_eligible`, `::test_recipe_missing_one_of_several_selected_preferences_is_excluded` | `tests/integration/test_event_configuration_and_filtering_views.py::test_suggestions_filters_by_preferences_with_and_semantics` | `event_configuration_and_filtering.feature` → `Scenario: Combine Anlassart and multiple preferences` |
| 4 — No optional filters | `tests/unit/test_recipe_classification.py::test_no_filters_active_the_recipe_is_eligible`; `tests/unit/test_services.py::test_all_recipes_are_suggested_when_no_filters_are_active` | `tests/integration/test_event_configuration_and_filtering_views.py::test_suggestions_with_no_optional_filters_returns_all_recipes` | `event_configuration_and_filtering.feature` → `Scenario: No optional filters` |
| 5 — No matching recipe | `tests/unit/test_services.py::test_no_recipe_matches_the_active_filters` | `tests/integration/test_event_configuration_and_filtering_views.py::test_suggestions_shows_distinct_no_match_message_when_event_type_has_no_recipes` | `event_configuration_and_filtering.feature` → `Scenario: No matching recipe` |
| 6 — Invalid budget | — | (shared `EventInputForm` validation; see `001`'s Scenario 6 tests) | `event_configuration_and_filtering.feature` → `Scenario: Invalid budget` |
| 7 — Invalid number of guests | — | (shared `EventInputForm` validation; see `001`'s Scenario 7 tests) | `event_configuration_and_filtering.feature` → `Scenario: Invalid number of guests` |
| 8 — Change event configuration | — | `tests/integration/test_event_configuration_and_filtering_views.py::test_changing_event_configuration_resets_previously_confirmed_recipe` | `event_configuration_and_filtering.feature` → `Scenario: Change event configuration` |

Not tied to one numbered scenario, but exercised throughout:

| Requirement | Test |
|---|---|
| `EventInputForm` enforces the 0-4 preference cap (`spec.md` §4) | `tests/integration/test_event_configuration_and_filtering_views.py::test_event_input_rejects_more_than_four_preferences` |
| The event-input page offers the seeded Anlassart/preference choices | `tests/integration/test_event_configuration_and_filtering_views.py::test_event_input_form_offers_the_seeded_event_type_and_preference_choices` |
| Seed data (`EventType`, `Preference`, recipe associations) | `tests/integration/test_seed_data.py` (all) |

## `CLAUDE.md` core business rules — current coverage

Only rules the Working Skeleton actually exercises are covered by tests today; the rest are
explicitly out of the Working Skeleton's scope (`spec.md` §3) and remain **not yet implemented**,
pending the full MVP feature spec.

| Rule | Status | Test |
|---|---|---|
| 1. Guest count must be a positive whole number | Implemented | `test_working_skeleton_views.py::test_reject_invalid_guest_count_shows_validation_message` |
| 2. Maximum budget must be greater than zero | Implemented | `test_working_skeleton_views.py::test_reject_invalid_budget_shows_validation_message` |
| 3. Use decimal arithmetic for money and quantities | Implemented (`Decimal` throughout `domain.py`) | `tests/unit/test_domain.py` (all) |
| 4. MVP currency is CHF | Implemented (display only; no multi-currency logic exists to test) | — |
| 5. A recipe must contain at least one ingredient | Holds for the three mock recipes; not enforced by a validator (no recipe authoring/import exists yet) | — |
| 6-11. Product article number, package quantity/price, `measuredIn`/`soldIn`, unit conversion out of scope | Implemented for the mock dataset | `tests/unit/test_exporters.py::test_export_contains_expected_values` |
| 12-13. Preference/event-type filtering | Implemented by `specs/002-mvp-event-configuration-and-filtering` (`Recipe.matches_classification`) | `tests/unit/test_recipe_classification.py`, `tests/unit/test_services.py`, `event_configuration_and_filtering.feature` |
| 14. Single-recipe suggestions must not exceed the request budget | **Superseded for the MVP**: `specs/002-mvp-event-configuration-and-filtering` removes budget-based suggestion eligibility outright (issue #8) — `spec.md` §6: "Budget does not filter recipe eligibility." The Working Skeleton's own 70%-of-budget cap no longer applies | `tests/unit/test_services.py::test_all_recipes_are_suggested_when_no_filters_are_active` |
| 15. One or more recipes may be selected | **Narrowed**: Working Skeleton allows selecting exactly one (`spec.md` §7 Scenario 2) | `test_working_skeleton_views.py::test_happy_path_end_to_end` |
| 16-20. Aggregation, package rounding, line cost, total cost, cost per guest | Implemented | `tests/unit/test_domain.py` |
| 21-23. `BudgetStatus`, over-budget confirmation | **Not implemented** — deferred to the full MVP feature (`plan.md` §6) | — |
| 24-25. Removing a procurement line, exporting only remaining lines | **Not implemented** — no stock-removal step exists yet | — |
| 26-27. Recipe XML import, no prices in XML | **Not implemented** — mock data only, no XML importer yet | — |
| 28. Serialize the confirmed draft only through `JsonProcurementOrderExporter` | Implemented | `tests/unit/test_exporters.py`, `test_working_skeleton_views.py::test_happy_path_end_to_end` |

## Export contract

| Requirement | Test |
|---|---|
| JSON order-draft matches `specs/001-working-skeleton/contracts/order-draft.md` | `tests/unit/test_exporters.py` (all), `test_working_skeleton_views.py::test_happy_path_end_to_end` |
| No price fields in the exported JSON | `tests/unit/test_exporters.py::test_export_contains_no_price_fields` |

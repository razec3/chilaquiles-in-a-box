# Working Skeleton Tasks

This file contains concrete implementation tasks derived from [`spec.md`](./spec.md) and [`plan.md`](./plan.md).

## Preparation

- [x] Complete the technical implementation plan. — `plan.md`
- [x] Identify the Working Skeleton subset of the existing domain model. — `data-model.md`
- [x] Define the required API/interface contracts. — `plan.md` §6 (page routes), `contracts/order-draft.md`
- [x] Define the JSON order-draft contract. — `contracts/order-draft.md`
- [x] Create mock data consistent with the domain model. — `Code/event_in_a_box/mock_data.py`
- [x] Confirm that the mock data supports all acceptance scenarios. — see `plan.md` §5; exercised by `tests/acceptance/features/working_skeleton.feature`

## Implementation

- [x] Implement event input handling. — `views.event_input`, `Code/templates/event_in_a_box/event.html`
- [x] Implement mock recipe proposal retrieval/generation. — `mock_data.py`, `repositories.MockRecipeRepository`, `services.find_recipe_suggestions`
- [x] Implement ingredient scaling by number of guests. — `domain.AperoPackageCalculator.calculate`
- [x] Implement ingredient-to-product mapping for the Working Skeleton. — `mock_data.py` (each `Ingredient` references one `Product`)
- [x] Implement purchasable packing-unit rounding. — `domain.AperoPackageCalculator.calculate`
- [x] Implement proposal/order price calculation. — `domain.AperoPackageCalculator.calculate`
- [x] Implement the one-recipe selection flow. — `views.select_recipe`, `services.PlanningSession`
- [x] Implement order-draft generation after confirmation. — `views.confirm_recipe`, `views.order_review`
- [x] Implement JSON order-draft generation and download. — `exporters.JsonProcurementOrderExporter`, `views.download_order`
- [x] Implement invalid-input handling. — `views.event_input` (form validation, re-renders with message)
- [x] Implement the no-valid-recipe case. — `services.find_recipe_suggestions`, `views.suggestions`

## Validation

- [x] Execute all acceptance scenarios from `spec.md`. — `Code/tests/acceptance/features/working_skeleton.feature`
- [x] Confirm the complete flow works locally without manual modification of application data. — verified via `docker compose run --rm web pytest` and a manual walkthrough (see completion report)
- [ ] Complete `checklists/technical-validation.md`. — not created; the Working Skeleton uses the `spec.md` §7 acceptance criteria and the automated test suite as its validation record instead of a separate manual checklist. Revisit if a manual sign-off checklist is explicitly wanted.

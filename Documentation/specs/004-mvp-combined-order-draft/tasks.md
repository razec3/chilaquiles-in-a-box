# Tasks: Combined Order Draft

Derived from [`spec.md`](./spec.md), [`plan.md`](./plan.md), and [`data-model.md`](./data-model.md).
Ordered by dependency; assumes `003`'s tasks are complete.

## Preparation

- [ ] Confirm with @razec3 whether this feature intentionally has no download action
      (`plan.md` §6 TODO).

## Views/templates

- [ ] Update the order-review view to resolve `selected_recipe_ids` (plural) to `Recipe` objects
      and call `calculator.calculate(selected_recipes, planning_request)` once.
- [ ] Update `order.html`: one row per `ProductRequirement` (product name, required packs, line
      price), overall total, rounded to CHF 0.01.
- [ ] Gate the view on ≥1 selected recipe (redirect to suggestions otherwise, consistent with `003`).

## Tests

- [ ] Integration test: combined draft for 2+ recipes sharing a product shows the aggregated pack
      count and price (not the sum of two independently-rounded lines).
- [ ] Integration test: draft is inaccessible with zero recipes selected.
- [ ] Integration test: draft recalculates when selection changes between two page loads.
- [ ] Acceptance tests: `Code/tests/acceptance/features/combined_order_draft.feature` covering
      `spec.md` §7 Scenarios 1–6.
- [ ] Update `Documentation/Testing/traceability.md`.

## Validation

- [ ] Run the full test suite.
- [ ] Manual walkthrough: select 2+ recipes with a shared product, confirm the combined draft
      matches hand-calculated totals.

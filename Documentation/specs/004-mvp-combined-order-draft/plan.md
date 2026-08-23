# Implementation Plan: Combined Order Draft

Behavioral requirements: [`spec.md`](./spec.md). Domain subset: [`data-model.md`](./data-model.md).
Extends [`003-mvp-multi-recipe-selection-and-budget/plan.md`](../003-mvp-multi-recipe-selection-and-budget/plan.md).

## 1. Components/layers involved

| Layer | Responsibility |
|---|---|
| Frontend | Rework `order.html` (currently single-recipe, Working Skeleton-era) to list one row per `ProductRequirement`: product name, required packs, line price, overall total — for the *combined* selection. |
| API / Backend | `views.order_review` (or a renamed successor) reads `selected_recipe_ids` (plural, from `003`) instead of a single `selected_recipe_id`, resolves each to a `Recipe`, and calls `calculator.calculate(selected_recipes, planning_request)` once. |
| Application / Domain Logic | None new — see `data-model.md` §1/§4. |
| Domain Model | Unchanged from `003`. |
| Data Source | Unchanged. |
| Backend Response | Server-rendered HTML, same pattern as the Working Skeleton's order view. |
| Frontend Result | One combined order draft table, auto-reflecting the current selection every time the page is loaded (no client-side caching of a stale draft). |

## 2. Data flow

```text
GET /order/  (successor to the Working Skeleton's order_review)
  selected_recipes = [repository.get_by_id(id) for id in session.selected_recipe_ids]
  package = calculator.calculate(selected_recipes, planning_request)
  render order.html: package.product_requirements, package.total_purchase_cost
```

No POST/confirm step is required to *reach* this view in this feature (contrast with the Working
Skeleton's `confirm_recipe` step) — `003`'s "proceed to final order" action is the only gate,
already covered there. Whether a distinct confirm/accept action still exists is `005`'s concern
(see that feature's `plan.md` for the flagged CLAUDE.md "final review and acceptance or rejection"
gap).

## 3. Domain logic responsibilities

None beyond what `AperoPackageCalculator.calculate` already does. This is the primary reason this
feature is low-risk: the aggregation-before-rounding logic this feature's acceptance scenarios test
(`spec.md` §7 Scenarios 2/3) already exists and is already unit-tested
(`Code/tests/unit/test_domain.py::test_shared_products_are_aggregated_before_package_rounding`) for
the general N-recipe case, even though the Working Skeleton UI only ever invoked it with one recipe.

## 4. Frontend/backend responsibilities

Backend computes and rounds everything; frontend renders the table. No new client-side logic.

## 5. Mock-data strategy

Unchanged from `002`/`003`.

## 6. Interfaces/contracts required

None — still server-rendered HTML, no new JSON contract. (The JSON *export* contract itself is
`005`'s concern, since this feature has no export/download action of its own — `spec.md` for this
feature does not mention downloading; that remains the Working Skeleton's `download_order` until
`005` supersedes it.)

<!-- TODO: confirm the download action is intentionally absent from this feature (i.e., a user can
view the combined draft here but must reach 005's final-order view to export it), rather than an
oversight. Not a contradiction, just worth an explicit product confirmation since the Working
Skeleton's order view *did* have a download action at the equivalent step. -->

## 7. Testing approach

- Unit: none new (covered by existing `AperoPackageCalculator` tests).
- Integration: `views.order_review` renders the correct combined totals for 2+ selected recipes
  sharing a product; view is inaccessible with zero selected recipes.
- Acceptance: `spec.md` §7 Scenarios 1–6 in a new
  `Code/tests/acceptance/features/combined_order_draft.feature`.

## 8. Implementation sequence

1. Confirm the §6 TODO (download action placement) with @razec3.
2. Update the order view to accept N selected recipes via `003`'s session state.
3. Update `order.html` for the multi-line combined draft.
4. Integration tests.
5. Acceptance tests.
6. Update `Documentation/Testing/traceability.md`.

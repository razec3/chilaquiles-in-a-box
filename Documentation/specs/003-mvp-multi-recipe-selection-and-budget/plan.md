# Implementation Plan: Multi-Recipe Selection and Budget Feedback

Behavioral requirements: [`spec.md`](./spec.md). Domain subset: [`data-model.md`](./data-model.md).
Extends [`002-mvp-event-configuration-and-filtering/plan.md`](../002-mvp-event-configuration-and-filtering/plan.md).

## 1. Components/layers involved

| Layer | Responsibility |
|---|---|
| Frontend | Rework `suggestions.html` into a multi-select list: each card shows name, standalone price, preference indicators, and a selection control (checkbox, not a radio). Add a persistent financial summary region (Einstandspreis / Marge / Budgetauslastung) that updates after each selection change. `recipe.html` becomes a pure read-only detail view reachable from any card without altering selection. |
| API / Backend | `views.suggestions` computes standalone price per recipe (`calculate([recipe], request)`) for display, independent of selection state. A new endpoint toggles a recipe's selection (replacing the WS `select_recipe`/`confirm_recipe` per-recipe flow — see §3). `views.recipe_detail` no longer mutates session state. |
| Application / Domain Logic | `domain.AperoPackage` gains `remaining_budget`/`budget_status` (see `data-model.md` §3). `services.py` gains a Budgetauslastung calculation (percentage + color band) as a plain function, not a domain-model field. |
| Domain Model | See `data-model.md`. No calculator changes — `AperoPackageCalculator.calculate` already aggregates correctly for N recipes. |
| Data Source | Unchanged from `002`. |
| Backend Response | Server-rendered HTML; selection toggling can be a simple POST + redirect (no JS framework required, consistent with CLAUDE.md's "no separate SPA" rule) or a small unobtrusive JS enhancement, per the existing `event-form.js` pattern. |
| Frontend Result | Suggestion list with live financial summary; read-only recipe detail; "proceed to final order" action, enabled only once ≥1 recipe is selected. |

## 2. Data flow

```text
GET /suggestions/  (recipes filtered per 002)
  for each eligible recipe:
    standalone_package = calculator.calculate([recipe], planning_request)
  combined_package = calculator.calculate(selected_recipes, planning_request)  (selected_recipes may be empty)
  budgetauslastung = combined_package.total_purchase_cost / planning_request.maximum_budget  (0 if none selected)

POST /suggestions/<id>/toggle/
  -> PlanningSession.toggle_recipe(id)  (add if absent, remove if present)
  -> redirect /suggestions/  (recalculated)
```

## 3. Session-state change (blocking design decision, low risk)

Replace `PlanningSession`'s `selected_recipe_id: str | None` with `selected_recipe_ids: list[str]`
(or a set). This affects:

- `services.PlanningSession`: `select_recipe`/`selected_recipe_id` → `toggle_recipe`/`selected_recipe_ids`.
- `views.select_recipe`/`confirm_recipe` (WS): replaced by a single toggle view. WS's separate
  "select → view detail → confirm" per-recipe sequence no longer matches this feature's flow
  (selection happens directly from the list; detail viewing is a side trip that does not select).
- `order_review`/`confirm_order`/`order_confirmation`/`download_order` (WS, `004`/`005` territory):
  must read `selected_recipe_ids` (plural) instead of a single id. Tracked in `004`'s plan, not
  re-specified here.

This is a controlled, backward-incompatible change to `services.py`'s session schema — acceptable
per `spec.md` §6 ("no persistence across page refreshes or application restarts is required"), so
no migration of stored session data is needed.

## 4. Frontend/backend responsibilities

Backend computes and rounds all monetary values (CLAUDE.md rule 3: decimal arithmetic). Frontend
only renders precomputed values and the color band; it must not recompute Budgetauslastung
client-side beyond the existing minor `event-form.js`-style live hint pattern, to avoid duplicating
business logic in two places.

## 5. Mock-data strategy

Unchanged from `002` §5 — this feature adds no new data requirements beyond what `002` already
seeds/mocks. Standalone pricing uses the same `Product`/`Ingredient` data.

## 6. Interfaces/contracts required

No new JSON/HTTP contract; still server-rendered HTML. No `contracts/` directory for this feature.

**Flagged, not resolved here — over-budget confirmation:** `spec.md` §7 Scenarios 5/6 state that
selection "remains allowed" in yellow/red Budgetauslastung states with no mention of a confirmation
step. CLAUDE.md business rule 23 and the MVP scope list require "continuation after an over-budget
warning and **explicit user confirmation**." `spec.md` for this feature does not identify itself as
superseding that CLAUDE.md rule (nor could it, per CLAUDE.md's precedence section, which only lets
feature specs supersede *Working Skeleton* behavior, not CLAUDE.md's own business rules). This is
a genuine, unresolved contradiction — see the review report's "Critical inconsistencies." Do not
implement either a silent bypass or an unspecified confirmation dialog; escalate to @razec3 first.

## 7. Testing approach

- Unit: standalone price is selection-independent; combined price aggregates correctly for 2+
  recipes (already covered by existing `test_domain.py` multi-recipe tests — extend if needed);
  Budgetauslastung percentage and color-band boundaries (exactly 70%, exactly 100%, just above each).
- Integration: selection toggling persists across requests; deselecting removes a recipe's
  contribution; "proceed to final order" is gated on ≥1 selection.
- Acceptance: `spec.md` §7 Scenarios 1–10 in a new
  `Code/tests/acceptance/features/multi_recipe_selection_and_budget.feature`.

## 8. Implementation sequence

1. Resolve the §3 session-schema change and the §6 over-budget-confirmation question (blocking).
2. Extend `domain.AperoPackage` with `remaining_budget`/`budget_status`.
3. Add the Budgetauslastung calculation function (`services.py` or a small new module).
4. Replace single-selection session state with multi-selection (`services.py`).
5. Update `views.suggestions` (standalone prices, combined summary, toggle endpoint) and
   `views.recipe_detail` (read-only, no selection side effects).
6. Update templates: suggestion cards (checkbox + price + preference indicators), financial summary
   region, recipe detail.
7. Unit tests for Budgetauslastung/`BudgetStatus`.
8. Integration tests for the toggle flow.
9. Acceptance tests for `spec.md` §7.
10. Update `Documentation/Testing/traceability.md`.

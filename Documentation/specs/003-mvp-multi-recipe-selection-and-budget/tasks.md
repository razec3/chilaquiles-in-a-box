# Tasks: Multi-Recipe Selection and Budget Feedback

Derived from [`spec.md`](./spec.md), [`plan.md`](./plan.md), and [`data-model.md`](./data-model.md).
Ordered by dependency; assumes `002`'s tasks are complete.

## Preparation (blocking — human decisions)

- [ ] Get @razec3 decision on the over-budget-confirmation contradiction between CLAUDE.md rule 23
      and `spec.md`'s "selection remains allowed" language (`plan.md` §6).
- [ ] Get @EdiAnderegg sign-off on retiring/keeping `BudgetStatus` alongside the new Budgetauslastung
      concept (`data-model.md` §3).

## Domain layer

- [ ] Add `remaining_budget: Decimal` and `budget_status: BudgetStatus` to `domain.AperoPackage`,
      computed in `AperoPackageCalculator.calculate`.
- [ ] Add the `BudgetStatus` enum to `domain.py` (`WITHIN_BUDGET`/`LIMIT_REACHED`/`OVER_BUDGET`).
- [ ] Unit tests: `WITHIN_BUDGET` (< budget), `LIMIT_REACHED` (= budget exactly), `OVER_BUDGET`
      (> budget); `remaining_budget` can be negative when over budget.

## Application layer

- [ ] Add a Budgetauslastung calculation (`Einstandspreis / Budget`, clamped/handled for a
      zero-budget edge case) with a 3-band color classification (green ≤70%, yellow >70%–≤100%,
      red >100%).
- [ ] Unit tests: boundary values at exactly 70% and exactly 100%.
- [ ] Replace `PlanningSession.selected_recipe_id` with `selected_recipe_ids` (list/set); add
      `toggle_recipe(id)`.
- [ ] Update `services.find_recipe_suggestions` (or successor) so it no longer applies the 70%
      cap for selection purposes if the `002`-blocking decision confirmed its removal.

## Views/templates

- [ ] `views.suggestions`: compute and pass standalone price per eligible recipe, the combined
      package for the current selection, and the Budgetauslastung band.
- [ ] New/updated selection-toggle view (`POST /suggestions/<id>/toggle/` or equivalent).
- [ ] `views.recipe_detail`: read-only, reachable for any recipe id without requiring prior
      selection; no session mutation.
- [ ] Update `suggestions.html`: selection checkboxes, standalone price, preference indicator
      badges (Vegetarisch/Schweizer Produkt/Nachhaltige Packung/Saisonal), financial summary
      (Einstandspreis neutral, Marge neutral-unless-negative-then-red, Budgetauslastung
      color-coded), "proceed to final order" action (disabled/hidden until ≥1 selected).
- [ ] Update `recipe.html`: remove select/confirm actions, keep only ingredient list scaled to
      guest count and a "back to suggestions" action.

## Tests

- [ ] Integration tests: toggle add/remove persists across requests; combined totals recalculate
      correctly for 2+ recipes sharing a product; "proceed to final order" gating.
- [ ] Acceptance tests: `Code/tests/acceptance/features/multi_recipe_selection_and_budget.feature`
      covering `spec.md` §7 Scenarios 1–10.
- [ ] Update `Documentation/Testing/traceability.md`.

## Validation

- [ ] Run the full test suite.
- [ ] Manual smartphone-width walkthrough: select 2+ recipes, confirm live financial updates,
      deselect one, view a recipe detail without losing selection, cross all three budget bands.

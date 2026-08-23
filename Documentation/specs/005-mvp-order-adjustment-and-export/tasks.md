# Tasks: Order Adjustment and Export

Derived from [`spec.md`](./spec.md), [`plan.md`](./plan.md), [`data-model.md`](./data-model.md), and
[`contracts/order-draft.md`](./contracts/order-draft.md). Ordered by dependency; assumes `004`'s
tasks are complete.

## Preparation (blocking — human decisions)

- [ ] Get @razec3 approval that manual pack-quantity adjustment is in scope, despite being absent
      from CLAUDE.md's MVP scope list and business rules (`data-model.md` §2).
- [ ] Get @EdiAnderegg decision on the model shape for quantity adjustment/soft-removal: Option A
      (extend `ProcurementOrderLine`/`ProcurementOrderDraft`) or Option B (application-layer
      overlay) (`data-model.md` §2).
- [ ] Get @razec3 decision on the over-budget export confirmation contradiction (`plan.md` §6) —
      apply consistently with the same decision already needed for `003`/`004`.
- [ ] Get @razec3 confirmation on whether "final review and acceptance or rejection" (CLAUDE.md MVP
      scope) requires a dedicated step beyond download/navigate-back (`plan.md` §6).
- [ ] Get @EdiAnderegg sign-off on the proposed `contracts/order-draft.md` v2 field names.

## Domain/application layer

- [ ] Implement the approved quantity-adjustment/soft-removal model (Option A or B).
- [ ] Implement quantity validation: positive integers only; reject 0, negative, non-integer,
      keeping the previous valid value.
- [ ] Implement recalculation of line totals, draft total, remaining budget, budget status, and
      Budgetauslastung from only the active lines' current quantities.
- [ ] Implement reset of adjustment state when `selected_recipe_ids` changes (hook into `003`'s
      toggle endpoint).
- [ ] Unit tests: quantity increase/decrease recalculation; rejection cases; removed-line exclusion
      from totals; reset-on-selection-change.

## Export layer

- [ ] Update `JsonProcurementOrderExporter` for the v2 contract: `recipeNames` (array),
      `packageCount` = active quantity, removed lines excluded, no price fields.
- [ ] Unit tests: export reflects adjusted quantities; export excludes removed lines; export
      contains no price fields (extend existing `test_exporters.py` patterns).
- [ ] Update `Code/tests/fixtures/` for the new export shape.

## Views/templates

- [ ] Quantity-change endpoint (per line, validated, recalculates, redirects/re-renders).
- [ ] Remove-line endpoint (soft removal, recalculates, redirects/re-renders).
- [ ] Update `order.html`: editable quantity input per active line; crossed-out calculated value
      when it differs from the active value; crossed-out/inactive styling for removed lines;
      remove action; live financial summary; download action gated on ≥1 active line.
- [ ] Update/replace the download endpoint for the v2 export shape and the new availability gate.

## Tests

- [ ] Integration tests: quantity change persists across requests; remove persists across requests;
      both reset when the recipe selection changes; download unavailable with zero active lines;
      download succeeds and reflects current state while over budget.
- [ ] Acceptance tests: `Code/tests/acceptance/features/order_adjustment_and_export.feature`
      covering `spec.md` §7 Scenarios 1–12.
- [ ] Export contract tests against the fixtures per `CLAUDE.md`'s "Export contract tests" section.
- [ ] Update `Documentation/Testing/traceability.md`.

## Validation

- [ ] Run the full test suite.
- [ ] Manual walkthrough: reduce a quantity, increase a quantity, restore a calculated quantity
      manually, remove a product, navigate away and back (changes persist), change recipe selection
      (changes discarded), download twice after two different edits and diff the files, drive the
      order over 100% budget and confirm export still succeeds.

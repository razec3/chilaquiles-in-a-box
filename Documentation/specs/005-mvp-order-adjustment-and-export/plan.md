# Implementation Plan: Order Adjustment and Export

Behavioral requirements: [`spec.md`](./spec.md). Domain subset: [`data-model.md`](./data-model.md).
Extends [`004-mvp-combined-order-draft/plan.md`](../004-mvp-combined-order-draft/plan.md).

**This feature has the largest number of unresolved items in this review** — see `data-model.md`
§2 (manual quantity adjustment absent from CLAUDE.md/the class model) and §6 below (over-budget
export confirmation contradiction). Do not begin implementation before those are resolved.

## 1. Components/layers involved

| Layer | Responsibility |
|---|---|
| Frontend | Final order view becomes editable: per-line quantity input (integer, min 1), remove action, crossed-out styling for removed lines and for the calculated-vs-actual value when they differ. Live financial summary (Einstandspreis/Marge/Budgetauslastung), same color rules as `003`. Download action, gated on ≥1 active line. |
| API / Backend | New endpoints: set quantity for a line, remove a line. Both recalculate and re-render (or return updated fragment data) without a full "confirm" round trip. `views.download_order` (successor) exports the *current* active-line state. |
| Application / Domain Logic | Whichever option from `data-model.md` §2 is approved: either extend `ProcurementOrderLine`/`ProcurementOrderDraft` (Option A) or add an application-layer per-line overlay applied on top of a freshly calculated draft (Option B). Either way, recalculation must re-derive Einstandspreis/Marge/Budgetauslastung from only the active (non-removed) lines' current (adjusted or calculated) quantities. |
| Domain Model | See `data-model.md` §2 — blocked on a decision. |
| Data Source | Unchanged from `002`–`004`. |
| Backend Response | HTML for the order view; JSON (with `Content-Disposition: attachment`) for the download endpoint, per `contracts/order-draft.md`. |
| Frontend Result | Editable order table; repeatable JSON download reflecting the latest edits. |

## 2. Data flow

```text
GET /order/
  package = calculator.calculate(selected_recipes, planning_request)   # the calculated baseline
  draft = apply_adjustments(package, session.order_adjustments)        # §data-model.md option A/B
  render order.html: draft.active_lines, draft.total, draft.remaining_budget, draft.budget_status

POST /order/lines/<article_number>/quantity/   {quantity: int}
  validate quantity is a positive integer -> reject silently keeping prior value, or accept
  session.order_adjustments[article_number].actual_count = quantity
  -> redirect /order/ (recalculated)

POST /order/lines/<article_number>/remove/
  session.order_adjustments[article_number].removed = True
  -> redirect /order/ (recalculated)

GET /order/download/
  draft = apply_adjustments(...)
  if draft.active_lines is empty -> 404/redirect (export unavailable)
  document = JsonProcurementOrderExporter().export(draft)
```

Selection-change reset (from `003`'s toggle endpoint): clear `session.order_adjustments` whenever
`selected_recipe_ids` changes (`spec.md` §6, Scenario 12).

## 3. Domain logic responsibilities

- Quantity validation: positive integer only (CLAUDE.md rule 3's decimal-arithmetic guidance
  applies to money/measured quantities; *pack counts* are already integers in the canonical model,
  so this is a straightforward integer validator, not a new numeric type).
- Recalculation: line total = actual (or calculated, if unadjusted) package count × purchase price
  per package; draft total = sum over active lines only; remaining budget / budget status /
  Budgetauslastung recompute from that total, reusing `003`'s Budgetauslastung function.

## 4. Frontend/backend responsibilities

All validation and recalculation happen server-side (quantity rejection, totals). The frontend
only reflects state and submits quantity/removal changes — no business logic duplicated client-side.

## 5. Mock-data strategy

Unchanged from `002`–`004`.

## 6. Interfaces/contracts required

See [`contracts/order-draft.md`](./contracts/order-draft.md) — this feature changes the JSON export
contract from `001-working-skeleton/contracts/order-draft.md`: multiple recipes, adjusted package
counts instead of calculated ones, and removed lines excluded. This is a **breaking export-contract
change**, which CLAUDE.md explicitly requires be documented (`CLAUDE.md` "Export contract tests").

**Flagged, not resolved here — export while over budget:** `spec.md` §7 Scenario 7 allows JSON
download when Budgetauslastung exceeds 100% with no confirmation step ("the system allows the
download... the red warning state remains visible"). This is the same CLAUDE.md rule-23 / MVP-scope
"explicit user confirmation" contradiction flagged in `003`'s and `004`'s plans, here at its most
consequential point — the point where a real file is produced. Resolve once, at the product level
(@razec3), and apply consistently across `003`/`004`/`005` rather than deciding independently per
feature.

**Also flagged — "final review and acceptance or rejection":** CLAUDE.md's MVP scope explicitly
lists this as in-scope, but no spec among `002`–`005` describes a distinct accept/reject action;
the closest analog is "download = acceptance" and "change event inputs = rejection" (implicit, not
stated). Confirm whether that implicit reading satisfies the requirement, or whether a dedicated
review/accept step (similar to the Working Skeleton's `order_confirmation` screen) must be kept.

## 7. Testing approach

- Unit: quantity validation (accepts positive integers, rejects 0/negative/non-integer); line total
  recalculation for calculated vs. adjusted quantity; removed-line exclusion from totals; JSON
  export field mapping including adjusted quantities and removed-line exclusion (extend
  `test_exporters.py`).
- Integration: quantity-change and remove endpoints persist across requests within the same
  selection; adjustments reset when selection changes; download unavailable with zero active lines;
  download available and correct while over budget.
- Acceptance: `spec.md` §7 Scenarios 1–12 in a new
  `Code/tests/acceptance/features/order_adjustment_and_export.feature`.
- Export contract tests: update/extend `Code/tests/fixtures/` per CLAUDE.md's "Export contract
  tests" guidance, reflecting the new JSON shape in `contracts/order-draft.md`.

## 8. Implementation sequence

1. Resolve `data-model.md` §2 (quantity-adjustment model shape) and this file's §6 items
   (over-budget export confirmation; final review/acceptance semantics) — all blocking.
2. Implement the chosen adjustment-state mechanism (Option A or B).
3. Implement quantity-set and remove endpoints with validation.
4. Wire selection-change reset of adjustments (touches `003`'s toggle endpoint).
5. Update `order.html`: editable quantities, crossed-out calculated/removed styling, live totals.
6. Update `JsonProcurementOrderExporter`/`download_order` for the new export shape.
7. Unit tests (validation, recalculation, export mapping).
8. Integration tests (endpoints, reset-on-selection-change, download gating).
9. Acceptance tests for `spec.md` §7.
10. Update export fixtures and `contracts/order-draft.md` cross-references.
11. Update `Documentation/Testing/traceability.md`.

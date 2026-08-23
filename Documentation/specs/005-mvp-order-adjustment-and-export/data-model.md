# Data Model: Order Adjustment and Export

Documents only the subset of the authoritative class model
([`Documentation/Architecture/event-in-a-box-domain-model-and-erm.md`](../../Architecture/event-in-a-box-domain-model-and-erm.md))
needed by this feature. Extends [`004-mvp-combined-order-draft/data-model.md`](../004-mvp-combined-order-draft/data-model.md).

## 1. Classes used

| Canonical class | Used here | Notes |
|---|---|---|
| `AperoPackage` | Yes, as the recalculation source | Provides `productRequirements` (the *calculated* baseline) whenever the recipe selection changes — this feature discards manual edits when that happens (`spec.md` §6 "State behavior"). |
| `ProcurementOrderDraft` | Yes, but **needs an extension not in the canonical model** — see §2 | `removeLine(articleNumber)` and `recalculate()` already exist in the class model and directly support the "remove a product" half of this feature. |
| `ProcurementOrderLine` | Yes, but **needs an extension not in the canonical model** — see §2 | The canonical fields (`orderedPackageCount`, `estimatedLineTotal`, ...) represent one *calculated* value per product. This feature requires tracking a **user-adjusted quantity distinct from the calculated one**, which the canonical model does not have a field for. |
| `IProcurementOrderExporter` / `JsonProcurementOrderExporter` | Yes | Exports the *current active* draft state — see `contracts/order-draft.md`. |
| `BudgetStatus` | Yes | Recalculated after every manual change, same trichotomy as `003`. |

## 2. Domain-model gap: manual quantity adjustment is not in CLAUDE.md or the class model

**This is the most significant finding of this review.** Neither `CLAUDE.md`'s business rules
(1–28) nor the canonical class model define manual pack-quantity editing. CLAUDE.md's MVP scope
list enumerates only:

> - removal of procurement lines for products already in stock
> - final review and acceptance or rejection
> - JSON procurement-order export

There is no bullet for "manually change the ordered quantity of a line." The canonical
`ProcurementOrderLine` has exactly one package-count field (`orderedPackageCount`) and exactly one
total field (`estimatedLineTotal`) — a single calculated snapshot, not a calculated-vs-actual pair.
`spec.md` §4/§6 for this feature requires **both** to be simultaneously representable (the
calculated value shown "subdued/crossed-out," the user-adjusted value shown as active), plus a
"removed but still visible, crossed out" state distinct from `ProcurementOrderDraft.removeLine`'s
implied hard removal (CLAUDE.md rule 24/25 talk about lines "remaining" in the draft, implying
removed lines are gone, not retained-but-inactive).

This needs a product/architecture decision before implementation, not a silent model change. Two
non-exclusive extension shapes, **neither approved here**:

**Option A — extend the canonical class model** (`ProcurementOrderLine` gains fields):

```text
ProcurementOrderLine
  + calculatedPackageCount: int      (renamed from orderedPackageCount; the system's recommendation)
  + actualPackageCount: int          (the user-adjusted, exportable quantity; defaults to calculatedPackageCount)
  + isRemoved: bool                  (soft-removal flag; excluded from totals/export but still rendered)
```

**Option B — keep the canonical model as the calculated snapshot, add an application-layer overlay**
(a per-line "adjustment" dict in `services.py`/session state: `{article_number: {actual_count: int,
removed: bool}}`), applied on top of a freshly recalculated `ProcurementOrderDraft` each time it is
rendered or exported. This keeps `ProcurementOrderLine` a pure projection (CLAUDE.md OOD rule:
"Treat `ProcurementOrderLine` as an order projection, not as a second calculation model") at the
cost of the overlay itself becoming a small second piece of state to keep in sync.

<!-- TODO/DECISION (@razec3 for scope, @EdiAnderegg for model shape): approve manual quantity
adjustment as in-scope (it is required by spec.md but absent from CLAUDE.md's MVP scope list and
business rules), and choose Option A, Option B, or an alternative. This blocks implementation of
the quantity-adjustment half of this feature (Scenarios 1-4) until resolved. Line removal alone
(Scenarios 5, 10) is already supported by the canonical model via ProcurementOrderDraft.removeLine,
modulo the "still visible, crossed out" display requirement, which also needs the soft-removal
concept from Option A or B rather than a hard removal. -->

## 3. Relationships/cardinalities used

Unchanged from the canonical model: `ProcurementOrderDraft *-- "0..*" ProcurementOrderLine`.

## 4. Feature-specific constraints

- Manual quantities must be positive integers; 0 and negative values are rejected, previous valid
  quantity remains active (`spec.md` §6/§7 Scenario 3).
- Removing a line excludes it from totals, Einstandspreis, Marge, Budgetauslastung, and export, but
  keeps it visible/crossed-out; it cannot be directly restored (`spec.md` §6).
- Manual adjustments and removals persist across navigation while the recipe selection is
  unchanged; they are discarded when the recipe selection changes (`spec.md` §6 "State behavior";
  CLAUDE.md rule 24 for the removal half).
- JSON export is available only when the active (non-removed) order has ≥1 product
  (`spec.md` §6 "JSON export"; extends the Working Skeleton's export gate).
- Export contains the *actual* (user-adjusted) package count, not the calculated one, and excludes
  removed lines and all price fields — see `contracts/order-draft.md`.

## 5. Session/application state

Whichever option from §2 is chosen, this state belongs in the Django session, mirroring
`PlanningSession`'s existing pattern in `services.py`. `spec.md` §6 requires manual changes to
survive in-app navigation (Scenario 11) but does not require surviving a browser refresh or an
application restart — session-backed storage satisfies the navigation requirement "for free" and
is not required to do more than that.

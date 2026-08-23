# Data Model: Combined Order Draft

Documents only the subset of the authoritative class model
([`Documentation/Architecture/event-in-a-box-domain-model-and-erm.md`](../../Architecture/event-in-a-box-domain-model-and-erm.md))
needed by this feature. Extends [`003-mvp-multi-recipe-selection-and-budget/data-model.md`](../003-mvp-multi-recipe-selection-and-budget/data-model.md).

## 1. Classes used

| Canonical class | Used here | Notes |
|---|---|---|
| `AperoPackage` | Unchanged (from `003`) | This feature's "combined order draft" is a **display** of the already-calculated `AperoPackage` for the current selection — `spec.md` introduces no new calculation. |
| `ProductRequirement` | Unchanged | `product`, `requiredQuantity`, `requiredPackageCount`, `lineCost` — exactly the fields `spec.md` §4 asks to display (product name, packs, line price) plus the overall total (`AperoPackage.totalPurchaseCost`). |
| `ProcurementOrderDraft` / `ProcurementOrderLine` | **Not required by this feature** | This feature is read-only/auto-recalculating (`spec.md` §5: "updates automatically... replaces the previous... draft"), with no line removal or quantity editing — those are introduced by `005`. Per the Working Skeleton precedent (`001-working-skeleton/data-model.md` §1), this feature can therefore keep reading directly from `AperoPackage.productRequirements`, exactly as the Working Skeleton's order view did for a single recipe, just now fed by `AperoPackageCalculator.calculate(selected_recipes, request)` for N recipes. |

No calculator or domain-model changes are required for this feature — `AperoPackageCalculator.calculate` already aggregates shared products across N recipes before rounding (`domain.py`, already implemented and unit-tested in the Working Skeleton for the multi-recipe path).

## 2. Relationships/cardinalities used

Unchanged from `003`. This feature is purely a new view over the existing `AperoPackage` produced
from the current `selected_recipe_ids` session state (`003`'s `plan.md` §3).

## 3. Feature-specific constraints

- Requirements for the same product across selected recipes are summed **before** packing-unit
  conversion (already implemented; `spec.md` §6, Scenario 2 restates the existing behavior for
  this view).
- The order draft recalculates automatically whenever the recipe selection changes, discarding any
  prior state (`spec.md` §6) — trivially true here since this feature holds no separate mutable
  state; the "order draft" is always freshly derived. This constraint becomes meaningful only once
  `005` introduces manual adjustments that must be discarded on selection change.
- Monetary totals rounded to CHF 0.01 (already implemented via `domain.round_money`).
- The final order view is accessible only when ≥1 recipe is selected (same gate as `003`).

## 4. What this feature does *not* need from the domain model

Because this feature is read-only, it does not need `ProcurementOrderDraft.removeLine()`,
`recalculate()`, or the `ProcurementOrderLine` projection type at all. Introducing them here would
be premature per CLAUDE.md's YAGNI guidance — they are `005`'s concern. Keep `views.order_review`
(or its successor) reading `AperoPackage.productRequirements` directly, as the Working Skeleton
already does, just for a multi-recipe `AperoPackage`.

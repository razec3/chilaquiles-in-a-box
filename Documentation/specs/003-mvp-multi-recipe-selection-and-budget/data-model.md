# Data Model: Multi-Recipe Selection and Budget Feedback

Documents only the subset of the authoritative class model
([`Documentation/Architecture/event-in-a-box-domain-model-and-erm.md`](../../Architecture/event-in-a-box-domain-model-and-erm.md))
needed by this feature. Extends [`002-mvp-event-configuration-and-filtering/data-model.md`](../002-mvp-event-configuration-and-filtering/data-model.md).

## 1. Classes used

| Canonical class | Used here | Notes |
|---|---|---|
| `Recipe` | Unchanged (from `002`) | Standalone price uses the same `Recipe.matchesClassification`-filtered set from `002`. |
| `AperoPackageCalculator` | Yes — `calculate(recipes, request)` | Used twice per request: once per recipe alone (standalone price) and once for the full selected set (combined financials). Same method both times — CLAUDE.md OOD rule "use the same `calculate(recipes, request)` path for one recipe and multiple recipes." No new calculator logic is required; multi-recipe aggregation is already implemented in `domain.py::AperoPackageCalculator.calculate` (it loops over all input recipes' ingredients regardless of count). |
| `AperoPackage` | Yes, extended | This feature is the first to require `budgetStatus` and `remainingBudget`, which the Working Skeleton subset deliberately excluded (`001-working-skeleton/data-model.md` §2). Both must be added to `event_in_a_box.domain.AperoPackage`. |
| `BudgetStatus` | Yes, new | `WITHIN_BUDGET` / `LIMIT_REACHED` / `OVER_BUDGET`, per the canonical enum. See §3 for how this relates to the feature's own Budgetauslastung concept. |
| `ProductRequirement` | Unchanged | Already implemented. |

## 2. Relationships/cardinalities used

- `AperoPackage o-- "1..*" Recipe` — a package is calculated from one or more recipes; this feature
  is the first to actually exercise the "more than one" case in the UI (WS only ever selected one).
- `AperoPackage --> "1" BudgetStatus`.

## 3. Terminology mapping and a genuine model gap: Budgetauslastung

`spec.md` §6 defines:

```text
Einstandspreis     = current combined purchase cost      == AperoPackage.totalPurchaseCost
Marge              = Budget - Einstandspreis              == AperoPackage.remainingBudget
Budgetauslastung   = Einstandspreis / Budget               -- NOT in the canonical class model
```

`Budgetauslastung` is a **continuous percentage** with a three-band color scheme (≤70% green,
>70%–≤100% yellow, >100% red). The canonical `BudgetStatus` enum is a **discrete trichotomy** based
on exact comparison to 100% of budget (`WITHIN_BUDGET`: total < max; `LIMIT_REACHED`: total = max;
`OVER_BUDGET`: total > max). These are not the same taxonomy, but they are compatible, not
contradictory:

| Budgetauslastung band | `BudgetStatus` |
|---|---|
| Green (≤70%) | `WITHIN_BUDGET` |
| Yellow (>70%–≤100%) | `WITHIN_BUDGET` (70%< x <100%) or `LIMIT_REACHED` (exactly 100%) |
| Red (>100%) | `OVER_BUDGET` |

Recommendation (not yet approved): keep `BudgetStatus` as-is on `AperoPackage` for the CLAUDE.md
business-rule-23 over-budget-confirmation gate (see `plan.md` §6 — itself unresolved), and add
`Budgetauslastung` as a **derived, UI-only value** computed at the view/service layer
(`Einstandspreis / Budget`, not stored on the domain model), with its own three-band color mapping.
Do not rename or repurpose `BudgetStatus`'s thresholds to match 70%/100% — that would silently
change a CLAUDE.md-defined enum's meaning.

<!-- TODO (@EdiAnderegg): confirm this Budgetauslastung/BudgetStatus coexistence is the intended
design, or whether BudgetStatus should be retired in favor of Budgetauslastung's bands entirely. -->

## 4. Feature-specific constraints

- Standalone recipe price = `calculate([recipe], request).total_purchase_cost` for the *full* guest
  count, independent of what else is selected (`spec.md` §7 Scenario 2).
- Combined financials = `calculate(selected_recipes, request)` — shared products aggregated before
  rounding (already implemented, not new logic).
- At least one recipe must be selected before the final order is reachable (`spec.md` §6/§8;
  CLAUDE.md's canonical model §6 rule 15, restated).
- Selecting/deselecting recalculates combined financials immediately; opening/closing recipe detail
  does not (`spec.md` §6).
- Recipe detail view is read-only and does not offer select/deselect controls (`spec.md` §5) —
  distinct from the Working Skeleton's `recipe_detail` view, which is coupled to the single-selection
  session flow. See `plan.md` §3 for the required session-state change.

## 5. Session/application state (not part of the persisted domain model)

The Working Skeleton's `PlanningSession` stores a single `selected_recipe_id: str | None`. This
feature requires a **set of selected recipe ids**, since CLAUDE.md's "removal of procurement lines"
and this feature's deselection both operate on a growing/shrinking selection. This is an
application-layer change (`services.py`), not a domain-model change — `data-model.md`'s classes are
unaffected; see `plan.md` §3.

# Working Skeleton Data Model

The project already has an existing class model, documented in full at
[`Documentation/Architecture/event-in-a-box-domain-model-and-erm.md`](../../Architecture/event-in-a-box-domain-model-and-erm.md).
This file documents only the subset and constraints relevant to the Working Skeleton; it does not
redefine the complete domain model.

## 1. Domain Concepts Used

The canonical class names used by the Working Skeleton, and where they diverge from the full model:

| Canonical class | Used by the Working Skeleton | Notes |
|---|---|---|
| `PlanningRequest` | Yes | Only `guestCount` and `maximumBudget`. `selectedPreferences` and `eventType` are not collected (out of scope). |
| `Recipe` | Yes | Only `id`, `name`, `description`, `ingredients`. `supportedEventTypes` and `preferences` are not used (no filtering by event type/preference in the Working Skeleton). |
| `Ingredient` | Yes | Unchanged: `product`, `quantityPerGuest`. |
| `Product` | Yes | Unchanged: `articleNumber`, `name`, `packageQuantity`, `measuredIn`, `soldIn`, `purchasePricePerPackage`. |
| `MeasurementUnit` | Yes | Unchanged enumeration. |
| `PackageType` | Yes | Unchanged enumeration. |
| `ProductRequirement` | Yes | Unchanged: `product`, `requiredQuantity`, `requiredPackageCount`, `lineCost`. |
| `AperoPackage` | Yes | `recipes`, `productRequirements`, `totalPurchaseCost`, `purchaseCostPerGuest`, `maximumBudget`. `budgetStatus`/`remainingBudget` in the full sense (relative to 100% of budget) are **not** used; see §2. |
| `AperoPackageCalculator` | Yes | Only `calculate(recipes, request)`, used with exactly one recipe at a time (the Working Skeleton allows selecting only one recipe). |
| `BudgetStatus` | No | Deferred — see §2 and `plan.md` §6. |
| `ProcurementOrderDraft` | No | The Working Skeleton has no line-removal ("already in stock") step, so there is no mutable, recalculating draft object. The order draft view reads directly from the calculated `AperoPackage`. |
| `ProcurementOrderLine` | Conceptually, not as a class | The JSON export (`contracts/order-draft.md`) mirrors this shape (article number, product name, package quantity, measurement unit, ordered package count, sales-package type) but is produced directly from `ProductRequirement` by the exporter, without an intermediate mutable line object. |
| `IProcurementOrderExporter` / `JsonProcurementOrderExporter` | Yes | Implemented as specified; exports directly from the calculated `AperoPackage`. |
| `IRecipeRepository` / `IProductRepository` | Yes, mocked | `MockRecipeRepository` and `MockProductRepository` implement these interfaces over the in-memory mock dataset (`plan.md` §5), matching the interface shape the future `DatabaseRecipeRepository`/`TransgourmetProductRepository` will implement. |
| `EventType`, `Preference`, `PreferenceCategory` | No | The Working Skeleton has no event-type or preference filtering (out of scope per `spec.md` §3). |
| `IRecipeImporter` / `XmlRecipeImporter` | No | Mock data is hard-coded; XML import is out of scope. |

## 2. Working Skeleton Constraints

- Ingredient quantities scale linearly with `guestCount`: `requiredQuantity = ingredient.quantityPerGuest * request.guestCount`.
- For the Working Skeleton, each ingredient maps to exactly one purchasable product (already true of the canonical `Ingredient → Product` association; the Working Skeleton does not add a second mapping layer).
- `requiredPackageCount = ceiling(requiredQuantity / product.packageQuantity)`, `lineCost = requiredPackageCount * product.purchasePricePerPackage` — identical to the canonical `AperoPackageCalculator` rules (CLAUDE.md business rules 17-18).
- **Deviation from the canonical `BudgetStatus`:** the Working Skeleton does not compute `WITHIN_BUDGET`/`LIMIT_REACHED`/`OVER_BUDGET` against the full `maximumBudget`, and does not implement the over-budget confirmation flow (business rules 21-23). Instead, `spec.md` defines a single, stricter constraint: a recipe is only ever *suggested* if `totalPurchaseCost <= maximumBudget * 0.70`. This 70%-of-budget "purchase limit" is a Working-Skeleton-specific concept, applied in `event_in_a_box/services.py::find_recipe_suggestions`, not in `AperoPackageCalculator` itself. See `plan.md` §6 for the follow-up decision this raises for the full MVP.
- The order draft (JSON export) contains the product's `articleNumber`, `name`, `packageQuantity`, `measuredIn`, `soldIn`, and the calculated `requiredPackageCount` — the product information the domain model already carries. Price information (`purchasePricePerPackage`, `lineCost`) is displayed in the UI but deliberately excluded from the exported JSON (`spec.md` Scenario 5).

## 3. JSON-Relevant Fields

See [`contracts/order-draft.md`](./contracts/order-draft.md) for the exact downloadable JSON structure, field names, and a worked example. In summary, each exported line carries `articleNumber`, `productName`, `packageQuantity`, `measuredIn`, `soldIn`, and `orderedPackageCount` — no price fields, per `spec.md` Scenario 5.

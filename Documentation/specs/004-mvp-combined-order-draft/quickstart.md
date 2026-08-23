# Quickstart: Combined Order Draft

Builds on [`003-mvp-multi-recipe-selection-and-budget/quickstart.md`](../003-mvp-multi-recipe-selection-and-budget/quickstart.md).

## Prerequisites / Installation / Start

Unchanged — see the `001`–`003` quickstarts.

## Verify the happy path

1. Select two or more recipes known (from the seed/mock data) to share at least one product.
2. Open the final order view. Confirm the shared product appears as a **single** line with the
   combined pack count (`spec.md` §7 Scenario 2), not one line per recipe.
3. Confirm the overall total equals the sum of the displayed line prices, rounded to CHF 0.01
   (`spec.md` §7 Scenario 5).
4. Return to the suggestion list, change the selection (add or remove a recipe), and reopen the
   final order view. Confirm the draft reflects the new selection (`spec.md` §7 Scenario 6).

## Troubleshooting

If a shared product still shows as two separate lines, check that the order view is calling
`AperoPackageCalculator.calculate` once with **all** selected recipes, not once per recipe.

# Quickstart: Order Adjustment and Export

Builds on [`004-mvp-combined-order-draft/quickstart.md`](../004-mvp-combined-order-draft/quickstart.md).

## Prerequisites / Installation / Start

Unchanged — see the `001`–`004` quickstarts.

## Verify the happy path

1. Reach the final order view with two or more selected recipes.
2. Reduce one line's quantity below its calculated value. Confirm: no warning is shown, the
   calculated value appears subdued/crossed-out, totals recalculate immediately
   (`spec.md` §7 Scenario 1).
3. Increase another line's quantity above its calculated value; confirm totals recalculate
   (`spec.md` §7 Scenario 2).
4. Attempt to set a quantity to `0`; confirm it is rejected and the previous value remains
   (`spec.md` §7 Scenario 3).
5. Manually set the adjusted line back to its original calculated value; confirm the
   subdued/crossed-out styling disappears (`spec.md` §7 Scenario 4).
6. Remove a product; confirm it remains visible, crossed out, contributes CHF 0, and is excluded
   from Einstandspreis/Marge/Budgetauslastung (`spec.md` §7 Scenario 5).
7. Download the JSON. Confirm it contains only active products with their current adjusted
   quantities, no price fields, and no removed products (`spec.md` §7 Scenario 8; see
   `contracts/order-draft.md`).
8. Make another edit and download again; confirm the new file reflects the latest state and the
   previously downloaded file is unaffected (`spec.md` §7 Scenario 9).
9. Navigate to a recipe detail view and back; confirm all manual changes are still present
   (`spec.md` §7 Scenario 11).
10. Return to the suggestion list and change the recipe selection; confirm manual changes are
    discarded and the draft recalculates from scratch (`spec.md` §7 Scenario 12).
11. Remove every product from the draft; confirm the download action becomes unavailable
    (`spec.md` §7 Scenario 10).
12. Drive Budgetauslastung above 100% (e.g. by increasing quantities); confirm the download still
    succeeds and the red state remains visible (`spec.md` §7 Scenario 7).

## Troubleshooting

If manual changes disappear on a simple page refresh, check that they are stored in the Django
session (server-side), not only in page-local JavaScript state.

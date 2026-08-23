# Quickstart: Multi-Recipe Selection and Budget Feedback

Builds on [`002-mvp-event-configuration-and-filtering/quickstart.md`](../002-mvp-event-configuration-and-filtering/quickstart.md).

## Prerequisites / Installation / Start

Unchanged — see the `001`/`002` quickstarts. No new services, ports, or environment variables.

## Verify the happy path

1. Configure a valid event (budget, guests, optional Anlassart/Präferenzen) and reach the
   suggestions page.
2. Confirm each recipe card shows its own standalone price and preference indicators.
3. Select two or more recipes. Confirm Einstandspreis, Marge, and Budgetauslastung appear and
   reflect the combined selection, not the sum of standalone prices where a product is shared
   (`spec.md` §7 Scenario 3 — pick two recipes known to share a product in the seed/mock data).
4. Open a recipe's detail view from the list; confirm it is read-only (no select/deselect control)
   and that returning to the list preserves the selection (`spec.md` §7 Scenario 8).
5. Deselect one recipe; confirm the financial summary recalculates immediately
   (`spec.md` §7 Scenario 7).
6. Drive the combined price past 70% and then past 100% of budget (e.g. by selecting enough
   recipes, or lowering the budget on the event input page) and confirm the yellow, then red,
   Budgetauslastung states — and that selection remains possible in both
   (`spec.md` §7 Scenarios 5/6).
7. With zero recipes selected, confirm the final-order action is unavailable
   (`spec.md` §7 Scenario 9); select one and confirm it becomes available
   (`spec.md` §7 Scenario 10).

## Troubleshooting

If Budgetauslastung never turns red in manual testing, lower the budget on the event input page —
`spec.md` places no constraint preventing an over-100% combination.

# MVP Feature Specification: Order Adjustment and Export

## 1. Purpose

This feature allows the user to modify the system-generated order draft before export.

The user can change actual pack quantities, remove products, observe the resulting financial impact, and download the current order draft as JSON.

---

## 2. Relationship to Working Skeleton

This feature extends the Working Skeleton order export by making the generated order draft editable before download.

The downloaded JSON must represent the current user-adjusted order, not necessarily the originally calculated recommendation.

---

## 3. User Flow

1. The user opens the final order view.
2. The system displays the calculated product quantities and prices.
3. The user may change the number of packs to purchase.
4. The user may remove products from the order.
5. The system recalculates financial values after each change.
6. The user may navigate away and return without losing manual adjustments, provided the recipe selection remains unchanged.
7. The user downloads the current order draft as JSON.
8. The user may make further changes and download the JSON again.

---

## 4. Final Order Display

For active products, the final order displays:

- Product name
- Calculated required number of packs
- Current actual number of packs to purchase
- Total price per product
- Overall total price

When the current quantity differs from the calculated quantity:

- The calculated quantity remains visible in a subdued/crossed-out style.
- The user-adjusted quantity is displayed as the active quantity.

When the current quantity equals the calculated quantity, the correction visualization does not need to be shown.

Removed products remain visible but are displayed as crossed out/inactive.

---

## 5. Financial Information

Manual order changes immediately update:

- Einstandspreis
- Marge
- Budgetauslastung
- Product totals
- Overall total price

Definitions remain:

- `Einstandspreis = current active order purchase cost`
- `Marge = Budget - Einstandspreis`
- `Budgetauslastung = Einstandspreis / Budget`

Budget status:

- Green: `≤ 70%`
- Yellow: `> 70% and ≤ 100%`
- Red: `> 100%`

Negative Marge is highlighted red.

Budget status never blocks order export.

---

## 6. Business Rules

### Quantity adjustment

- The user edits the actual number of packs to purchase.
- Manual order quantities must be positive integers.
- The user may reduce the quantity below the system-calculated requirement.
- No warning is required when ordering fewer packs than calculated.
- Quantity `0` cannot be entered as a quantity adjustment.
- Removing a product must use the separate remove action.
- No dedicated reset action is required.
- The user may manually restore the calculated quantity by entering it again.

### Product removal

- The user may remove a product from the order draft.
- A removed product remains visible as crossed out/inactive.
- A removed product contributes CHF 0 to the order.
- A removed product is excluded from:
  - product totals,
  - Einstandspreis,
  - Marge,
  - Budgetauslastung,
  - JSON export.
- A removed product cannot be directly restored in the MVP.

### State behavior

- Manual quantity adjustments and removals persist while the selected recipe set remains unchanged.
- Navigating away from and back to the final order does not reset these changes.
- If the selected recipe set changes, all manual order changes are discarded and the order draft is recalculated.
- If the user returns to the initial event configuration and changes any event input, all downstream order state is reset.
- No persistence across refreshes or application restarts is required.

### JSON export

- JSON export is available only when the active order contains at least one product.
- The JSON represents the state of the order draft at the moment of download.
- The user may download the JSON multiple times.
- A later download reflects later modifications.
- Previously downloaded files are not modified.
- JSON export remains available even when Budgetauslastung exceeds 100%.
- The JSON contains the required product information defined by the domain model.
- The JSON contains the actual number of packs to purchase.
- Removed products are not included.
- Price information is not included.

<!-- TODO: Replace generic "product information" with exact fields once the JSON contract is finalized. -->

---

## 7. Acceptance Criteria

### Scenario 1: Reduce pack quantity

**Given**

- The calculated quantity for a product is 3 packs.

**When**

- The user changes the quantity to 1 pack.

**Then**

- The active order quantity is 1 pack.
- The system accepts the change without warning.
- The calculated value of 3 packs remains visible in a subdued/crossed-out style.
- Product and financial totals are recalculated using 1 pack.

### Scenario 2: Increase pack quantity

**Given**

- The calculated quantity is 2 packs.

**When**

- The user changes the quantity to 4 packs.

**Then**

- The active order quantity is 4 packs.
- Product and financial totals are recalculated using 4 packs.

### Scenario 3: Reject invalid manual quantity

**Given**

- A product exists in the order draft.

**When**

- The user attempts to set the pack quantity to 0, a negative number, or a non-integer value.

**Then**

- The quantity change is rejected.
- The previous valid quantity remains active.

### Scenario 4: Restore calculated quantity manually

**Given**

- The calculated quantity is 3 packs.
- The user previously changed it to 1 pack.

**When**

- The user manually changes the quantity back to 3 packs.

**Then**

- The current quantity equals the calculated quantity.
- The correction visualization no longer needs to be displayed.

### Scenario 5: Remove a product

**Given**

- A product is active in the order draft.

**When**

- The user removes the product.

**Then**

- The product remains visible as crossed out/inactive.
- It contributes CHF 0.
- It is excluded from Einstandspreis and other financial calculations.
- It cannot be directly restored.

### Scenario 6: Recalculate financial state

**Given**

- An order draft is displayed.

**When**

- The user modifies a pack quantity or removes a product.

**Then**

- Product totals are recalculated.
- Overall Einstandspreis is recalculated.
- Marge is recalculated.
- Budgetauslastung is recalculated.
- The correct budget-status color is shown.

### Scenario 7: Export while over budget

**Given**

- Budgetauslastung is greater than 100%.

**When**

- The user requests the JSON download.

**Then**

- The system allows the download.
- The red warning state remains visible.

### Scenario 8: Download adjusted order

**Given**

- The user has manually modified the order draft.

**When**

- The user downloads the JSON.

**Then**

- The JSON contains the active products.
- The JSON contains their current user-adjusted pack quantities.
- Removed products are excluded.
- Price information is excluded.

### Scenario 9: Download again after modification

**Given**

- The user has already downloaded an order draft.
- The user subsequently modifies the current order.

**When**

- The user downloads the JSON again.

**Then**

- The new file reflects the current order state.
- The previously downloaded file is unaffected.

### Scenario 10: Empty active order

**Given**

- All products have been removed from the order draft.

**Then**

- JSON download is unavailable.

### Scenario 11: Preserve manual changes during navigation

**Given**

- The user has manually adjusted the order.
- The selected recipes remain unchanged.

**When**

- The user leaves the final order view and returns to it.

**Then**

- The manual quantity changes remain.
- Removed products remain removed.

### Scenario 12: Reset after recipe selection change

**Given**

- The user has manually adjusted the order.

**When**

- The selected recipe set changes.

**Then**

- Manual quantity changes are discarded.
- Removed-product state is discarded.
- The order draft is recalculated from the current recipe selection.

---

## 8. Definition of Done

This feature is done when the user can modify the calculated order draft, see the financial impact of those modifications immediately, remove products, retain manual changes while the recipe selection remains unchanged, and download the current adjusted order as JSON.
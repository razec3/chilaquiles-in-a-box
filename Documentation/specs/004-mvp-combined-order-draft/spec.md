# MVP Feature Specification: Combined Order Draft

## 1. Purpose

This feature converts the currently selected recipes into one combined order draft.

The system must consolidate shared product requirements across recipes before calculating purchasable packing units and prices.

---

## 2. Relationship to Previous Specifications

This feature extends the order-generation behavior introduced in the Working Skeleton.

Instead of generating an order from one selected recipe, the MVP generates one combined order draft from all currently selected recipes.

---

## 3. User Flow

1. The user selects one or more recipes.
2. The system combines the ingredient requirements of all selected recipes.
3. The system maps the combined requirements to purchasable products.
4. Requirements for the same product are aggregated.
5. The system converts combined product requirements to purchasable packing units.
6. The system calculates product totals and overall Einstandspreis.
7. The order draft updates automatically whenever the recipe selection changes.
8. Once at least one recipe is selected, the user can access the final order view.

---

## 4. Expected Order Draft

The order draft displays at least:

- Product name
- Required number of packs
- Total price per product
- Overall total price

The order draft is based on the currently selected recipes and the entered number of guests.

---

## 5. Business Rules

- Every selected recipe contributes its requirements for the full number of guests.
- Requirements for the same product across multiple recipes must be summed before packing-unit conversion.
- Packing units are always whole positive units.
- When the combined required quantity does not fit exactly into available packs, the number of packs is rounded upward.
- Product total price is based on the required number of purchasable packs.
- Overall Einstandspreis is the sum of the product totals in the order draft.
- Monetary totals are rounded to CHF 0.01.
- The order draft updates automatically when recipes are selected or deselected.
- Changing the selected recipe set replaces the previous calculated order draft with a newly calculated draft.
- Manual adjustments from a previous order state are discarded when the recipe selection changes.
- The final order is available only when at least one recipe is selected.
- Predefined/mock product and price data are used for the MVP.

---

## 6. Acceptance Criteria

### Scenario 1: Generate combined order from multiple recipes

**Given**

- Two or more recipes are selected.

**When**

- The system generates the order draft.

**Then**

- Requirements from all selected recipes are included.
- The order draft contains the resulting products and purchasable pack quantities.

### Scenario 2: Consolidate a shared product

**Given**

- Recipe A requires 0.6 kg of yogurt.
- Recipe B requires 0.6 kg of the same yogurt.
- Yogurt is sold in 1 kg packs.

**When**

- Both recipes are selected.

**Then**

- The combined requirement is 1.2 kg.
- The order draft contains 2 packs of yogurt.
- The system does not calculate one pack independently for each recipe before consolidation.

### Scenario 3: Round packing units upward

**Given**

- The combined requirement for a product is 1.2 kg.
- The product is sold in 1 kg packs.

**When**

- The order quantity is calculated.

**Then**

- The calculated order quantity is 2 packs.

### Scenario 4: Calculate product price

**Given**

- A product requires 2 packs.
- Mock price data are available for that product.

**Then**

- The total price for the product is based on 2 packs.

### Scenario 5: Calculate overall Einstandspreis

**Given**

- The order draft contains multiple products.

**When**

- Product totals are calculated.

**Then**

- Overall Einstandspreis equals the sum of all active product totals.
- The amount is rounded to CHF 0.01.

### Scenario 6: Update after recipe selection changes

**Given**

- An order draft exists.

**When**

- The user selects or deselects a recipe.

**Then**

- Combined requirements are recalculated.
- Packing units are recalculated.
- Product totals are recalculated.
- Overall Einstandspreis is recalculated.
- Any previous manual order adjustments are discarded.

---

## 7. Definition of Done

This feature is done when all selected recipes are converted into one automatically updated order draft that correctly consolidates shared product requirements, calculates purchasable packing units, and displays product and overall purchase costs.
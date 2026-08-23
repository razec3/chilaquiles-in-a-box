# MVP Feature Specification: Multi-Recipe Selection and Budget Feedback

## 1. Purpose

This feature allows the user to select multiple recipe proposals while continuously evaluating the financial impact of the selected combination.

The user must be able to understand the standalone cost of each recipe and the combined Einstandspreis, Marge, and Budgetauslastung of the current selection.

---

## 2. Relationship to Working Skeleton

This feature continues the Working Skeleton behavior change already made by `002`, which removes the restriction that limited displayed recipe proposals to a maximum cost of 70% of the entered budget (decision recorded in issue #8). No cap remains for this feature to remove.

For the MVP:

- Budget does not filter recipe proposals.
- Budget does not block recipe selection.
- A Budgetauslastung of 70% is a warning threshold.
- The user may select recipes resulting in a Budgetauslastung above 70% or above 100%.

This feature also supersedes the Working Skeleton restriction that only one recipe may be selected.

---

## 3. User Flow

1. The system displays all recipe proposals matching the event configuration.
2. Each recipe proposal displays its standalone purchase cost.
3. Each recipe proposal displays applicable preference indicators.
4. The user selects one or more recipes.
5. The system recalculates the combined financial state whenever the selection changes.
6. The user may deselect previously selected recipes.
7. The user may open a recipe detail view.
8. The recipe detail displays the recipe name, ingredients, and quantities scaled to the number of guests.
9. The user returns to the recipe proposal list without changing the selection.
10. Once at least one recipe is selected, the user may proceed to the final order.

---

## 4. Recipe Proposal Information

Each recipe proposal displays at least:

- Recipe name
- Standalone purchase cost
- Selection control
- Preference indicators for:
  - Vegetarisch
  - Schweizer Produkt
  - Nachhaltige Packung
  - Saisonal

Anlassart does not need to be displayed on the recipe proposal.

---

## 5. Recipe Detail

The recipe detail view is read-only.

It displays:

- Recipe name
- Required ingredients
- Ingredient quantities scaled to the full number of guests

The recipe cannot be selected or deselected from the detail view.

---

## 6. Financial Information

The recipe selection view displays:

- Einstandspreis
- Marge
- Budgetauslastung

Definitions:

- `Einstandspreis = current combined purchase cost`
- `Marge = Budget - Einstandspreis`
- `Budgetauslastung = Einstandspreis / Budget`

The Budgetauslastung status is:

| Budgetauslastung | Status |
|---|---|
| ≤ 70% | Green |
| > 70% and ≤ 100% | Yellow |
| > 100% | Red |

Budgetauslastung is the primary color-coded financial indicator.

Einstandspreis is displayed neutrally.

Marge is displayed neutrally unless negative, in which case it is highlighted red.

---

## 7. Business Rules

- The user may select multiple recipes.
- At least one recipe must be selected before proceeding to the final order.
- Every selected recipe is calculated for the full number of guests.
- The standalone price displayed on a recipe is the purchase cost if that recipe alone were prepared for all guests.
- Standalone recipe prices use purchasable packing units.
- Standalone recipe prices do not change based on which other recipes are selected.
- Combined financial calculations use the combined requirements of all selected recipes.
- Requirements for the same product are combined before packing-unit rounding.
- Selecting or deselecting a recipe immediately recalculates:
  - Einstandspreis,
  - Marge,
  - Budgetauslastung,
  - combined product requirements.
- Budget is informational and never prevents recipe selection.
- The user may exceed 70% Budgetauslastung.
- The user may exceed 100% Budgetauslastung.
- Opening and closing recipe details does not change recipe selections or financial calculations.
- Recipe selection and deselection are performed only from the recipe proposal list.
- The final order becomes accessible only when at least one recipe is selected.
- An explicit action is available to proceed to the final order.
- Changing the selected recipe set causes the order draft to be recalculated.
- Any previous manual order adjustments are discarded when the selected recipe set changes.

---

## 8. Acceptance Criteria

### Scenario 1: Select multiple recipes

**Given**

- Matching recipe proposals are displayed.

**When**

- The user selects two or more recipes.

**Then**

- All selected recipes remain selected.
- The combined financial state is recalculated.

### Scenario 2: Calculate standalone recipe price

**Given**

- A recipe has ingredient requirements for the entered number of guests.

**When**

- The system displays the recipe proposal.

**Then**

- The displayed recipe price represents the purchase cost of that recipe by itself.
- Required quantities are rounded to purchasable packing units before calculating the price.

### Scenario 3: Combine shared product requirements

**Given**

- Recipe A requires 0.6 kg of a product.
- Recipe B requires 0.6 kg of the same product.
- The product is sold in 1 kg packs.

**When**

- Both recipes are selected.

**Then**

- The combined requirement is 1.2 kg.
- The system calculates 2 packs.
- The combined Einstandspreis uses the cost of 2 packs.

### Scenario 4: Green budget state

**Given**

- The combined Einstandspreis is less than or equal to 70% of the budget.

**Then**

- Budgetauslastung is displayed with green status.

### Scenario 5: Yellow budget state

**Given**

- The combined Einstandspreis is greater than 70% and less than or equal to 100% of the budget.

**Then**

- Budgetauslastung is displayed with yellow status.
- Recipe selection remains allowed.

### Scenario 6: Red budget state

**Given**

- The combined Einstandspreis exceeds the budget.

**Then**

- Budgetauslastung is displayed with red status.
- Marge is negative and highlighted red.
- Recipe selection remains allowed.

### Scenario 7: Deselect recipe

**Given**

- Multiple recipes are selected.

**When**

- The user deselects one recipe.

**Then**

- That recipe's requirements are removed from the combined calculation.
- Packing-unit requirements are recalculated.
- Einstandspreis is recalculated.
- Marge is recalculated.
- Budgetauslastung is recalculated.

### Scenario 8: View recipe details

**Given**

- A recipe proposal is displayed.

**When**

- The user opens its detail view.

**Then**

- The recipe name is displayed.
- Its ingredients are displayed.
- Ingredient quantities are scaled to the full number of guests.
- The detail view does not change recipe selection.

### Scenario 9: Proceed without selection

**Given**

- No recipe is selected.

**Then**

- The final order is not accessible.
- The user cannot proceed to the final order.

### Scenario 10: Proceed with selection

**Given**

- At least one recipe is selected.

**Then**

- The final order becomes accessible.
- An explicit action allows the user to proceed to it.

---

## 9. Definition of Done

This feature is done when the user can select and deselect multiple recipes, inspect recipe details, see standalone recipe prices, and continuously see the correct combined Einstandspreis, Marge, and Budgetauslastung without budget thresholds blocking selection.
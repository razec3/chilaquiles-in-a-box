# Working Skeleton Specification

## 1. Purpose

The purpose of the Working Skeleton is to validate that the selected architecture and technology stack work end-to-end before implementing the complete MVP.

The Working Skeleton should implement the smallest meaningful user flow through all relevant system layers.

---

## 2. User Flow

The Working Skeleton covers the following minimal end-to-end flow.

<!-- input → proposal → selection → confirmation → order → download -->

1. The user enters budget and number of guests.
2. The user requests recipe proposals.
3. The system displays at least one recipe proposal.
4. The user selects a recipe proposal.
5. The system displays the selected recipe with its required ingredients and quantities.
6. The user confirms the selected recipe.
7. The system generates an order draft containing the required products and quantities and displays the total price.
8. The system makes the order draft available for download as JSON.

---

## 3. Scope

### In Scope

* Use mock recipe, ingredient, product, and price data consistent with the existing class model.
* Scale ingredient quantities according to the entered number of guests.
* Generate an order draft from the selected recipe.
* Calculate and display the total price using mock product prices.
* Export the order draft as JSON.

### Out of Scope

* Real recipe recommendation logic.
* Integration with real product or pricing data.
* Business rules not required for the Working Skeleton flow.

---

## 4. Input

| Input            | Type         | Required | Example |
| ---------------- | ------------ | -------: | ------: |
| Budget           | Number (CHF) |      Yes |    1000 |
| Number of guests | Integer      |      Yes |      50 |

---

## 5. Expected Output

The Working Skeleton produces the following outputs:

* At least one recipe proposal based on mock data.
* The selected recipe with its required ingredients and quantities scaled to the number of guests.
* The total price calculated using mock product prices.
* A downloadable JSON order draft containing the required order information.

The exact structure of the JSON order draft must be consistent with the existing domain model.

<!-- TODO: Once the relevant domain-model fields are finalized, align this section with contracts/order-draft.md. -->

---

## 6. Business Rules

The Working Skeleton must apply the following business rules:

* The number of guests must be a positive integer greater than 0.
* The budget must be greater than CHF 0.
* Ingredient quantities must scale linearly according to the number of guests.
* For the Working Skeleton, each ingredient maps to exactly one purchasable product.
* Required product quantities must be converted into purchasable packing units and rounded up to the next whole packing unit when necessary.
* The total price of every displayed recipe proposal must be calculated based on the required purchasable packing units.
* The total price must be less than or equal to 70% of the entered budget.
* Monetary totals must be rounded to CHF 0.01.
* The user can select exactly one recipe proposal.
* An order draft is generated only after the user confirms the selected recipe.
* If no recipe proposal satisfies the 70% budget constraint, the system must inform the user that no suitable recipe can be proposed for the given input.

<!-- TODO: Define exact user-facing validation/error messages only if exact wording is a requirement. -->

---

## 7. Acceptance Criteria

### Scenario 1: Generate recipe proposals with valid input

**Given**

* The budget is CHF 1'000.
* The number of guests is 50.
* Mock data consistent with the domain model is available.

**When**

* The user requests recipe proposals.

**Then**

* The system displays one or more recipe proposals.
* Every displayed recipe proposal has a total price less than or equal to CHF 700.
* The total price is calculated based on the required purchasable packing units.

### Scenario 2: View a selected recipe

**Given**

* One or more recipe proposals are displayed.

**When**

* The user selects one recipe proposal.

**Then**

* The system displays the selected recipe.
* The system displays its required ingredients.
* The displayed ingredient quantities are scaled according to the number of guests.
* Only one recipe proposal can be selected at a time.

### Scenario 3: Confirm a recipe and generate an order draft

**Given**

* The user has selected a recipe proposal.

**When**

* The user confirms the selected recipe.

**Then**

* The system generates an order draft.
* The system displays:

  * Product name.
  * Required number of packs.
  * Total price per product.
  * Overall total price.
* Monetary totals are rounded to CHF 0.01.
* A Download JSON action is available.

### Scenario 4: Calculate required packing units

**Given**

* A recipe requires 1.2 kg of an ingredient.
* The corresponding product is sold in 1 kg packs.

**When**

* The system calculates the required purchasable quantity.

**Then**

* The system requires 2 packs of the product.
* The product price and overall total price are calculated using 2 packs.

### Scenario 5: Download the order draft

**Given**

* An order draft has been generated.

**When**

* The user requests the JSON download.

**Then**

* The system downloads a JSON order draft.
* The JSON contains the product information required by the domain model.
* The JSON contains the required number of packs for each product.
* Price information is not included in the downloaded order draft.

<!-- TODO: Replace "product information required by the domain model" with exact fields once contracts/order-draft.md is finalized. -->

### Scenario 6: Reject invalid budget

**Given**

* The entered budget is less than or equal to CHF 0.

**When**

* The user attempts to request recipe proposals.

**Then**

* The system blocks the request.
* The system displays a validation message.

### Scenario 7: Reject invalid number of guests

**Given**

* The number of guests is 0, negative, or not an integer.

**When**

* The user attempts to request recipe proposals.

**Then**

* The system blocks the request.
* The system displays a validation message.

### Scenario 8: No recipe satisfies the budget constraint

**Given**

* The entered budget and number of guests are valid.
* No available recipe has a total purchase price less than or equal to 70% of the entered budget.

**When**

* The user requests recipe proposals.

**Then**

* No invalid recipe proposal is displayed.
* The system remains on the proposal view.
* The system informs the user that no suitable recipe can be proposed for the given input.

---

## 8. Definition of Done

The Working Skeleton is done when a user can run the application locally, enter a valid budget and number of guests, receive and select a mock recipe proposal, view the scaled ingredient quantities, confirm the recipe, see the generated order draft with calculated product quantities and prices, and download the order draft as JSON through the complete end-to-end system flow.

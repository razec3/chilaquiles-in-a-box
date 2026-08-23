# MVP Feature Specification: Event Configuration and Recipe Filtering

## 1. Purpose

This feature allows the user to define the basic event parameters and personal preferences that determine which recipes are eligible for the event.

The system must use these inputs to filter the available recipes and display all recipes matching the selected criteria.

---

## 2. Relationship to Working Skeleton

This feature extends the Working Skeleton event input by adding:

- Anlassart
- Persönliche Präferenzen
- Recipe filtering based on these inputs

The existing Working Skeleton requirements for budget and number of guests remain applicable unless explicitly superseded by another MVP feature specification.

This feature supersedes the Working Skeleton behavior that limits displayed recipe proposals to a maximum cost of 70% of the entered budget. As of this feature, budget does not filter recipe eligibility (§6); the 70%-of-budget suggestion cap no longer applies. (Decision recorded 2026-08-23, issue #8.)

---

## 3. User Flow

1. The user enters the event budget.
2. The user enters the number of guests.
3. The user optionally selects an Anlassart.
4. The user optionally selects one or more persönliche Präferenzen.
5. The user requests recipe proposals.
6. The system validates the required inputs.
7. The system filters the available recipes according to Anlassart and persönliche Präferenzen.
8. The system displays all matching recipe proposals.
9. If no recipe matches, the system informs the user and allows the user to return to the event configuration.

---

## 4. Inputs

| Input | Type | Required | Constraints |
|---|---|---:|---|
| Budget | Number (CHF) | Yes | Greater than CHF 0 |
| Number of guests | Integer | Yes | Greater than 0 |
| Anlassart | Predefined selection | No | Zero or one value |
| Persönliche Präferenzen | Multi-selection | No | Zero to four values |

### Anlassart

- The available Anlassarten are predefined for the MVP.
- The default value represents no specified Anlassart.
- When no Anlassart is specified, Anlassart does not restrict recipe eligibility.

<!-- TODO: Define the exact predefined Anlassart values. -->

### Persönliche Präferenzen

The MVP supports the following concepts:

- Vegetarisch
- Schweizer Produkt
- Nachhaltige Packung
- Saisonal

The exact UI labels may differ, but their meaning must remain equivalent.

The user may select zero to four preferences.

---

## 5. Expected Output

The system displays all recipes matching the selected filtering criteria.

If no recipe matches, the system displays an appropriate no-results message.

The system does not rank matching recipes.

---

## 6. Business Rules

- Budget is mandatory and must be greater than CHF 0.
- Number of guests is mandatory and must be a positive integer.
- Anlassart is optional.
- Persönliche Präferenzen are optional.
- A recipe may be associated with multiple Anlassarten.
- A recipe may be associated with multiple persönliche Präferenzen.
- For the MVP, Anlassart and persönliche Präferenzen are represented directly as recipe-level associations or tags.
- Anlassart acts as a hard filter when specified.
- Every selected persönliche Präferenz acts as a hard filter.
- A recipe is eligible only if it satisfies all active filtering conditions.
- If no Anlassart is specified, Anlassart does not restrict eligibility.
- If no persönliche Präferenzen are selected, preferences do not restrict eligibility.
- If neither Anlassart nor persönliche Präferenzen are specified, all available recipes are eligible.
- All eligible recipes are displayed.
- No additional ranking or recommendation logic is applied.
- Budget does not filter recipe eligibility.
- Recipe, ingredient, product, packing-unit, and price data are predefined/mock data consistent with the domain model.
- Event inputs cannot be changed after recipe selection has started without navigating back to the event configuration.
- If the user returns to the event configuration and changes any event input, all downstream state must be reset.
- No persistence across page refreshes or application restarts is required.

<!-- TODO: Define exact user-facing validation and no-results messages only if exact wording is a requirement. -->

---

## 7. Acceptance Criteria

### Scenario 1: Filter by Anlassart

**Given**

- The user has entered a valid budget and number of guests.
- The user selects an Anlassart.
- Recipes exist with different Anlassart associations.

**When**

- The user requests recipe proposals.

**Then**

- Only recipes associated with the selected Anlassart are displayed.

### Scenario 2: Filter by one preference

**Given**

- The user has entered valid required inputs.
- The user selects the preference `Vegetarisch`.

**When**

- The user requests recipe proposals.

**Then**

- Only recipes associated with `Vegetarisch` are displayed.

### Scenario 3: Combine Anlassart and multiple preferences

**Given**

- The user selects an Anlassart.
- The user selects `Vegetarisch` and `Saisonal`.

**When**

- The user requests recipe proposals.

**Then**

- A recipe is displayed only if it matches:
  - the selected Anlassart,
  - `Vegetarisch`,
  - and `Saisonal`.

### Scenario 4: No optional filters

**Given**

- The user has entered a valid budget and number of guests.
- No Anlassart is specified.
- No persönliche Präferenzen are selected.

**When**

- The user requests recipe proposals.

**Then**

- All available recipes are eligible for display.

### Scenario 5: No matching recipe

**Given**

- The entered inputs are valid.
- No available recipe satisfies all active filters.

**When**

- The user requests recipe proposals.

**Then**

- No non-matching recipe is displayed.
- The system informs the user that no matching recipe was found.
- The user can return to the event configuration.

### Scenario 6: Invalid budget

**Given**

- The budget is less than or equal to CHF 0.

**When**

- The user attempts to request recipe proposals.

**Then**

- The system blocks the request.
- A validation message is displayed.

### Scenario 7: Invalid number of guests

**Given**

- The number of guests is 0, negative, or not an integer.

**When**

- The user attempts to request recipe proposals.

**Then**

- The system blocks the request.
- A validation message is displayed.

### Scenario 8: Change event configuration

**Given**

- The user has already started recipe selection.

**When**

- The user navigates back to the event configuration and changes any event input.

**Then**

- Previously selected recipes are cleared.
- Manual order changes are cleared.
- The existing order draft is discarded.
- Recipe proposals are recalculated from the new event configuration.

---

## 8. Definition of Done

This feature is done when a user can configure the event, optionally select an Anlassart and zero to four persönliche Präferenzen, and receive all and only the recipes matching the active hard filters.
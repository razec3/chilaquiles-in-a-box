# Working Skeleton Data Model

The project already has an existing class model. This file documents only the subset and constraints relevant to the Working Skeleton.

<!-- TODO: Add a link/path to the authoritative UML/Mermaid class model. -->
<!-- TODO: Do not redefine the complete domain model here. Reference the authoritative model and document only what the Working Skeleton uses. -->

## 1. Domain Concepts Used

The Working Skeleton specification currently refers to these concepts:

- Recipe
- Ingredient
- Product
- Purchasable packing unit
- Order draft
- Price

<!-- TODO: Replace the terms above with the exact canonical class/entity names from the existing model if they differ. -->
<!-- TODO: Identify the relationships and fields required by the Working Skeleton. -->

## 2. Working Skeleton Constraints

The behavioral specification currently requires:

- Ingredient quantities scale according to the number of guests.
- For the Working Skeleton, each ingredient maps to exactly one purchasable product.
- A product has enough packing-unit information to calculate the required number of packs.
- Mock product data has enough price information to calculate total purchase price.
- The order draft contains the product information required by the domain model and the required number of packs.
- Price information is displayed in the UI but is not included in the downloadable JSON order draft.

<!-- TODO: Verify every statement above against the authoritative class model. -->

## 3. JSON-Relevant Fields

<!-- TODO: Fill once the relevant domain-model fields are finalized. -->
<!-- The exact downloadable JSON structure belongs in contracts/order-draft.md. -->

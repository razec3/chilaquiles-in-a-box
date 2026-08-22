Feature: Working Skeleton end-to-end flow

  Validates spec.md's acceptance criteria for the Working Skeleton: the
  smallest meaningful flow from event input to a downloadable order draft.

  Scenario: Generate recipe proposals with valid input
    Given the budget is "2000.00" and the number of guests is 50
    When the user requests recipe proposals
    Then the system displays one or more recipe proposals
    And every displayed recipe proposal has a total price of at most CHF 1400.00

  Scenario: View a selected recipe
    Given the budget is "2000.00" and the number of guests is 50
    And the user has requested recipe proposals
    When the user selects the recipe "zuercher-geschnetzeltes"
    Then the system displays the selected recipe with its scaled ingredients

  Scenario: Confirm a recipe and generate an order draft
    Given the budget is "2000.00" and the number of guests is 50
    And the user has selected the recipe "zuercher-geschnetzeltes"
    When the user confirms the selected recipe
    Then the system displays an order draft with product, packs, and total price

  Scenario: Download the order draft
    Given the budget is "2000.00" and the number of guests is 50
    And the user has confirmed the recipe "zuercher-geschnetzeltes"
    When the user requests the JSON download
    Then the system downloads a JSON order draft without price information

  Scenario: Reject invalid budget
    When the user requests recipe proposals with budget "0" and 50 guests
    Then the system blocks the request and shows a validation message

  Scenario: Reject invalid number of guests
    When the user requests recipe proposals with budget "2000.00" and 0 guests
    Then the system blocks the request and shows a validation message

  Scenario: No recipe satisfies the budget constraint
    Given the budget is "100.00" and the number of guests is 50
    When the user requests recipe proposals
    Then the system informs the user that no suitable recipe can be proposed

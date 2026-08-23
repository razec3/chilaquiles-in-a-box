Feature: Event configuration and recipe filtering

  Validates spec.md's acceptance criteria for filtering recipe suggestions by
  Anlassart and persönliche Präferenzen
  (Documentation/specs/002-mvp-event-configuration-and-filtering).

  Scenario: Filter by Anlassart
    Given the budget is "2000.00" and the number of guests is 50
    And the Anlassart "BUSINESS_APERO" is selected
    When the user requests recipe proposals
    Then only recipes for the Anlassart "BUSINESS_APERO" are displayed

  Scenario: Filter by one preference
    Given the budget is "2000.00" and the number of guests is 50
    And the preference "VEGETARISCH" is selected
    When the user requests recipe proposals
    Then only recipes with the preference "VEGETARISCH" are displayed

  Scenario: Combine Anlassart and multiple preferences
    Given the budget is "2000.00" and the number of guests is 50
    And the Anlassart "VEREINSANLASS" is selected
    And the preferences "VEGETARISCH" and "SAISONAL" are selected
    When the user requests recipe proposals
    Then only recipes matching the Anlassart "VEREINSANLASS" and every selected preference are displayed

  Scenario: No optional filters
    Given the budget is "2000.00" and the number of guests is 50
    When the user requests recipe proposals
    Then all available recipes are displayed

  Scenario: No matching recipe
    Given the budget is "2000.00" and the number of guests is 50
    And the Anlassart "BRUNCH" is selected
    When the user requests recipe proposals
    Then the system informs the user that no matching recipe was found
    And the user can return to the event configuration

  Scenario: Invalid budget
    When the user requests recipe proposals with budget "0" and 50 guests
    Then the system blocks the request and shows a validation message

  Scenario: Invalid number of guests
    When the user requests recipe proposals with budget "2000.00" and 0 guests
    Then the system blocks the request and shows a validation message

  Scenario: Change event configuration
    Given the budget is "2000.00" and the number of guests is 50
    And the user has confirmed the recipe "zuercher-geschnetzeltes"
    When the user changes the number of guests to 80
    Then the previously confirmed recipe selection is discarded

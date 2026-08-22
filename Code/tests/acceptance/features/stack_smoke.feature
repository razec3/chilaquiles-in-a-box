Feature: Application stack smoke test

  As a developer setting up Event in a Box
  I want to confirm the running application serves its start page
  So that I know the technical foundation is deployed correctly

  Scenario: Request the application start page
    Given the Event in a Box application is running
    When I request the start page
    Then I receive a successful response

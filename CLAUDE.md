# Event in a Box

## Purpose of this file

This file contains persistent operating instructions for Claude Code.

It is not a product specification and must not replace approved feature specs, architecture documents, Figma designs, or tests.

Claude must read this file before planning or modifying the project.

## Product purpose

Event in a Box helps restaurateurs plan an economically sensible Apero for an event in a few minutes.

The restaurateur provides:

- event type
- guest count
- maximum total budget
- preferences such as Vegan, Vegetarian, Regional, Seasonal, or Organic

The system calculates matching recipe suggestions from stored recipes and current Transgourmet product data. The restaurateur may combine multiple recipes, inspect the required products, remove products already in stock, review the final cost, and export the remaining procurement lines as JSON.

## Team authority

- Rodrigo owns product management, scope, prioritisation, and final product decisions.
- Eduard owns software architecture and implementation decisions within the approved product scope.
- Both may discuss product and technical alternatives.
- If a requirement is ambiguous or contradicts another approved artefact, stop and request a decision. Do not silently choose or expand the scope.

## MVP scope

The MVP supports:

- smartphone-first event planning
- event type, guest count, maximum budget, and preference input
- stored recipes with ingredients and classifications
- recipe import from XML
- mock or seeded Transgourmet products with package quantity, measurement unit, sales-package type, and purchase price
- zero to many matching single-recipe suggestions
- selection and calculation of one or more recipes
- aggregation of shared products before package rounding
- display of total purchase cost and purchase cost per guest
- `WITHIN_BUDGET`, `LIMIT_REACHED`, and `OVER_BUDGET` states
- continuation after an over-budget warning and explicit user confirmation
- removal of procurement lines for products already in stock
- final review and acceptance or rejection
- JSON procurement-order export

Explicitly out of scope unless a later approved spec introduces it:

- authentication or user accounts
- persisted restaurateur profiles
- inventory management or stock quantities
- order persistence or order history
- audit logging
- payments
- recipe selling prices
- live Transgourmet crawling
- a live Transgourmet product API
- non-JSON order export formats
- background workers or asynchronous processing
- microservices

## Technology stack

Backend and server-rendered frontend:

- Python
- Django
- Django Templates

Database:

- PostgreSQL

Application server:

- Gunicorn

Reverse proxy:

- Nginx

Infrastructure:

- Docker
- Docker Compose

Testing:

- pytest
- pytest-django
- pytest-bdd

Target deployment environment:

- provider-neutral Linux server environment
- Docker Compose deployment using the `nginx`, `web`, and `db` service topology

Do not introduce a separate SPA framework, REST API, or additional infrastructure unless an approved specification demonstrates the need.

## Canonical repository structure

Use this repository structure:

```text
.
├── CLAUDE.md
├── README.md
├── .env.example
├── .gitignore
├── compose.yaml
├── Code/
│   ├── Dockerfile
│   ├── manage.py
│   ├── pyproject.toml
│   ├── config/
│   ├── event_in_a_box/
│   ├── templates/
│   ├── static/
│   └── tests/
│       ├── unit/
│       ├── integration/
│       ├── acceptance/
│       │   ├── features/
│       │   └── step_definitions/
│       └── fixtures/
├── Infrastructure/
│   ├── nginx/
│   └── scripts/
├── Documentation/
│   ├── Architecture/
│   │   ├── ood.md
│   │   ├── erm.md
│   │   └── decisions/
│   ├── Design/
│   │   ├── figma.md
│   │   └── assets/
│   ├── Domain/
│   │   └── glossary.md
│   └── Testing/
│       ├── strategy.md
│       └── traceability.md
├── specs/
│   └── NNN-feature-name/
│       ├── spec.md
│       ├── plan.md
│       ├── tasks.md
│       ├── data-model.md
│       ├── research.md
│       ├── quickstart.md
│       ├── contracts/
│       └── checklists/
├── .specify/
│   ├── memory/
│   │   └── constitution.md
│   └── templates/
├── .github/
│   └── workflows/
│       └── ci.yml
├── Misc/
└── Presentation/
```

Do not create empty feature artefacts merely to fill this tree. Spec Kit creates the relevant files for each feature when needed.

## Artefact ownership and source of truth

### Feature specifications

Store feature-specific SDD artefacts in:

```text
specs/NNN-feature-name/
```

`spec.md` defines what users need and why. It must contain user stories, functional requirements, explicit out-of-scope statements, measurable acceptance criteria, and relevant edge cases. It must not contain implementation details.

`plan.md` defines how the approved feature will be implemented with the chosen stack and architecture.

`tasks.md` is derived from the approved spec and plan. Every implementation task must be traceable to a requirement or acceptance criterion.

`data-model.md`, `contracts/`, `research.md`, and `quickstart.md` are feature-local supporting documents created only when required.

### Constitution

Store permanent project principles in:

```text
.specify/memory/constitution.md
```

The constitution governs specification quality, testing, simplicity, mobile usability, security, and architectural discipline. It must not contain individual feature requirements.

### OOD and ERM

Store the approved project-wide architecture baseline in:

```text
Documentation/Architecture/ood.md
Documentation/Architecture/erm.md
```

Feature-specific model changes are first described in the relevant `specs/NNN-feature-name/data-model.md`. After approval, the project-wide OOD and ERM must be updated in the same change so that they remain consistent.

OOD classes are not automatically database entities. The ERM contains only persisted data.

### Figma design

Figma is the source of truth for approved UI and UX design.

Store the Figma project link and exact page or frame links in:

```text
Documentation/Design/figma.md
```

For every implemented screen, `figma.md` must identify:

- Figma page and frame name
- direct frame URL
- supported viewport or breakpoint
- design status such as Draft or Approved
- relevant interaction notes
- date of the last review

Store only exported assets required by the application in `Documentation/Design/assets/` or `Code/static/`. Do not commit a binary copy of the complete Figma project.

Each UI-related feature spec must reference the relevant Figma frames. If Figma and an approved specification contradict each other, stop and request clarification before implementing.

### Tests

Executable tests belong under `Code/tests/`. Acceptance criteria belong in `spec.md`; executable Given/When/Then scenarios belong in `Code/tests/acceptance/` and must reference their originating feature and acceptance criterion.

Maintain the mapping between requirements and automated tests in:

```text
Documentation/Testing/traceability.md
```

Avoid copying the same business rule into several documents. Use references where possible.

## Spec-driven development workflow

The required workflow is:

```text
Constitution
-> Specify
-> Clarify
-> Plan
-> Tasks
-> Analyse
-> Implement
-> Test
-> Converge
```

Recommended Spec Kit commands:

```text
/speckit.constitution
/speckit.specify
/speckit.clarify
/speckit.plan
/speckit.tasks
/speckit.analyze
/speckit.taskstoissues
/speckit.implement
/speckit.converge
```

Do not begin implementation from an informal prompt when a relevant approved spec exists.

Before implementing a task:

1. Read `CLAUDE.md`.
2. Read `.specify/memory/constitution.md`.
3. Read the relevant `spec.md`, `plan.md`, and `tasks.md`.
4. Read relevant OOD, ERM, architecture decisions, and Figma references.
5. Inspect existing code and tests.
6. Restate the acceptance criteria and affected business rules.
7. Identify the smallest vertical slice.
8. Add or update the protecting tests.
9. Implement only the approved scope.
10. Run focused tests and then the complete quality suite.
11. Check the implementation against the spec, plan, tasks, and design.
12. Summarise completed work, verification, and remaining concerns.

If the implementation reveals a missing or contradictory requirement, update or clarify the specification before changing code.

## Domain language

Use these terms consistently in code, tests, specifications, and UI copy.

### PlanningRequest

The event-planning input containing event type, guest count, maximum total budget, and selected preferences.

### Recipe

A stored Apero recipe definition. A recipe contains ingredients and classifications but no selling price.

### Ingredient

A recipe requirement referencing exactly one Transgourmet product and defining its quantity per guest.

### Product

An exact Transgourmet article with a unique article number, package quantity, measurement unit, sales-package type, and purchase price per package.

`measuredIn` defines how the package content is measured, such as `MILLILITRE`, `GRAM`, or `PIECE`. `soldIn` defines the physical sales package, such as `TUBE`, `BOTTLE`, `BAG`, or `BOX`.

Example: a 50 ml tube has `packageQuantity = 50`, `measuredIn = MILLILITRE`, and `soldIn = TUBE`.

### Preference

A filter or classification such as Vegan, Vegetarian, Regional, Seasonal, or Organic.

### AperoPackage

A calculated, read-only result for one or more selected recipes.

### ProductRequirement

An aggregated calculated requirement containing required quantity, rounded package count, and line cost for one product.

### ProcurementOrderDraft

The editable supplier order created from an Apero package. The restaurateur may remove lines for products already in stock.

### ProcurementOrderLine

A supplier-facing projection containing the Transgourmet article number, package quantity, measurement unit, ordered package count, sales-package type, and estimated cost information.

### BudgetStatus

One of `WITHIN_BUDGET`, `LIMIT_REACHED`, or `OVER_BUDGET`.

Budget status is informational. It controls presentation, not permission to export the order.

## Core business rules

1. Guest count must be a positive whole number.
2. Maximum budget must be greater than zero.
3. Use decimal arithmetic for money and quantities.
4. The MVP currency is CHF.
5. A recipe must contain at least one ingredient.
6. A product article number must be unique.
7. Package quantity and purchase price must be greater than zero.
8. Every product must define exactly one `measuredIn` value and one `soldIn` value.
9. An ingredient's quantity and the product's `packageQuantity` use the product's `measuredIn` unit.
10. `soldIn` describes the physical sales package and does not replace `measuredIn` or change the package-count formula.
11. Unit conversion is outside the MVP.
12. Every selected preference is a mandatory recipe filter.
13. A recipe suggestion must match the event type and selected preferences.
14. Single-recipe suggestions must not exceed the request budget.
15. One or more suggested recipes may be selected.
16. Shared products across selected recipes must be aggregated before package rounding.
17. Package count equals `ceiling(required quantity / package quantity)`.
18. Line cost equals `package count * purchase price per package`.
19. Total purchase cost is the sum of all product requirement line costs.
20. Purchase cost per guest equals `total purchase cost / guest count`.
21. A selected combination may exceed the budget.
22. An over-budget result must show the budget, total cost, and exceeded amount clearly.
23. An over-budget result may still create and export a procurement order after explicit confirmation.
24. Removing a procurement order line must not modify recipes or the calculated Apero package.
25. The exported order contains only the lines remaining in the draft.
26. Recipe XML references products by Transgourmet article number.
27. Recipe XML contains neither recipe selling prices nor copied product purchase prices.
28. Serialize the confirmed procurement draft only through `JsonProcurementOrderExporter`.

## Object-oriented design rules

Use conventional object-oriented design. Do not introduce Domain-Driven Design patterns merely for terminology or appearance.

- Keep the calculation algorithm in `AperoPackageCalculator`.
- Use the same `calculate(recipes, request)` path for one recipe and multiple recipes.
- Do not create separate suggestion and combination calculation algorithms.
- Keep `AperoPackage` and `ProductRequirement` read-only after calculation.
- Model `Product.measuredIn` with `MeasurementUnit` and `Product.soldIn` with `PackageType`.
- Map `ProductRequirement` to `ProcurementOrderLine` once when creating the draft, including package quantity, measurement unit, and sales-package type.
- Treat `ProcurementOrderLine` as an order projection, not as a second calculation model.
- Keep Django views and templates free of calculation and export logic.
- Depend on importer, exporter, and repository interfaces at format or storage boundaries.
- Keep JSON serialization inside `JsonProcurementOrderExporter`.
- Prefer one well-structured Django application for the MVP unless the implementation plan proves that another application boundary is necessary.

Do not add CQRS, event sourcing, a generic repository framework, a service bus, or unnecessary inheritance.

## Testing strategy

Tests are executable evidence that the implementation satisfies the specification. Tests must be deterministic, readable, and traceable to requirements.

### Unit tests

Unit-test pure business behaviour without Django or PostgreSQL where practical.

Required unit-test areas:

- input validation
- event type and preference matching
- guest-count scaling
- separation of `measuredIn` from `soldIn`
- calculation of a product sold as a 50 ml tube
- package rounding
- line-cost calculation
- cost per guest
- aggregation of shared products before rounding
- calculation of single and multiple recipes through the same method
- all three budget states
- mapping from `ProductRequirement` to `ProcurementOrderLine`
- recalculation after removing an order line
- JSON payload mapping

Do not unit-test trivial Django framework behaviour.

### Integration tests

Use integration tests when behaviour crosses a real boundary:

- Django ORM with PostgreSQL
- recipe and product repositories
- XML recipe import and article-number resolution
- Django views, forms, and database interaction
- migrations
- JSON file generation
- Nginx, Gunicorn, and Django smoke behaviour where appropriate

Use PostgreSQL in integration tests. Do not silently replace PostgreSQL-specific behaviour with SQLite.

### Acceptance tests

Use pytest-bdd for meaningful user-visible flows. Scenarios describe business behaviour, not implementation details.

The MVP acceptance suite must cover at least:

```gherkin
Feature: Plan an Apero package

  Scenario: Find matching recipes within the budget
  Scenario: Filter recipes by all selected preferences
  Scenario: Combine multiple selected recipes
  Scenario: Aggregate shared products before package rounding
  Scenario: Display required package counts with their sales-package type
  Scenario: Display a combination that exceeds the budget
  Scenario: Continue after confirming an over-budget warning
  Scenario: Remove products already available in stock
  Scenario: Export only the remaining procurement lines as JSON
```

Do not force every low-level rule into a BDD scenario. Use unit tests for calculation details.

### Export contract tests

Treat the JSON structure as an explicit versioned contract.

- Maintain representative JSON fixtures in `Code/tests/fixtures/`.
- Verify required fields, article numbers, package quantities, measurement units, package counts, sales-package types, currency, totals, and budget status.
- Use deterministic field ordering only if consumers require it.

### Test-first implementation rule

For every behaviour change:

1. Identify the acceptance criterion or business rule.
2. Select the lowest appropriate test level.
3. Add a failing test first when practical.
4. Implement the smallest change that makes the test pass.
5. Refactor only while tests remain green.
6. Run the focused tests.
7. Run the complete test suite before finishing.

Never weaken or delete a failing test merely to make the pipeline pass. Change a test only when the approved specification changed or the test was demonstrably incorrect.

## Infrastructure architecture

The intended topology is:

```text
Client
-> Nginx
-> Gunicorn
-> Django
-> PostgreSQL
```

Docker Compose must define, at minimum:

- `web`: Django running behind Gunicorn
- `db`: PostgreSQL with a persistent volume
- `nginx`: public reverse proxy serving static files and forwarding application requests

Infrastructure rules:

- Nginx is the only public application entry point in production.
- PostgreSQL must never be exposed publicly.
- Use environment variables for configuration.
- Commit `.env.example`; never commit real secrets or `.env`.
- Add health checks for PostgreSQL and the web application.
- Do not use fixed sleeps to coordinate service startup.
- Keep development sufficiently close to production to catch integration problems.
- Use named volumes for persistent PostgreSQL data.
- Collect Django static files during the production build or release process.
- Make database migrations an explicit deployment step.
- Keep the production deployment recoverable and documented.

Do not introduce Kubernetes, Redis, Celery, message brokers, or microservices without an approved requirement.

## Continuous integration

The GitHub Actions CI workflow must run for pull requests and pushes to the main integration branch.

The required quality gates are:

1. install locked dependencies
2. start PostgreSQL for integration tests
3. run formatting and lint checks configured by the project
4. run `python manage.py check`
5. run `python manage.py makemigrations --check --dry-run`
6. run unit tests
7. run integration tests
8. run acceptance tests
9. build the application container

A task is not complete while a required CI check fails.

Avoid arbitrary coverage targets. Prioritise coverage of business rules and failure paths. If the team introduces a coverage threshold, document it in `Documentation/Testing/strategy.md` and enforce it consistently in CI.

## Definition of Ready

A feature is ready for implementation only when:

- the user problem and value are clear
- scope and out-of-scope are explicit
- acceptance criteria are testable
- relevant edge cases are resolved
- Figma frames are linked for UI work
- OOD and ERM impact is identified
- security and data implications are identified
- Rodrigo has approved the product scope
- Eduard has approved the technical direction in the plan

## Definition of Done

A task or feature is done only when:

- implementation matches the approved spec and plan
- required unit, integration, acceptance, and contract tests pass
- the complete test suite passes
- CI passes
- migrations are included and verified when the ERM changes
- OOD, ERM, ADRs, Figma references, and traceability are updated when affected
- smartphone usability and readability are verified for affected screens
- no secrets or generated local files are committed
- no unapproved scope was added
- the implementation summary identifies verification performed and remaining limitations

## Code quality

- Prefer the simplest implementation that satisfies the approved specification.
- Apply KISS, YAGNI, separation of concerns, and explicit domain terminology.
- Keep functions and classes focused.
- Prefer descriptive names over generic technical names.
- Keep business calculations independent from HTTP, templates, XML, JSON, and database frameworks.
- Use Django migrations for schema changes.
- Do not manually edit generated migrations unless explicitly required and justified.
- Do not add a dependency without explaining its concrete need and obtaining approval.
- Preserve existing user changes and avoid unrelated refactoring.
- Do not create Git commits unless explicitly asked.

## Claude completion report

After completing an implementation task, report:

1. the spec and acceptance criteria implemented
2. the files changed
3. the tests added or changed
4. the commands executed and their results
5. any architectural or specification documents updated
6. unresolved risks, assumptions, or follow-up work

Never claim completion without reporting test evidence.

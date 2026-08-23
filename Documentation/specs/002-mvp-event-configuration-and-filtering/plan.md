# Implementation Plan: Event Configuration and Recipe Filtering

Behavioral requirements: [`spec.md`](./spec.md). Domain subset: [`data-model.md`](./data-model.md).
This plan extends [`001-working-skeleton/plan.md`](../001-working-skeleton/plan.md); it does not
repeat unchanged technical decisions from that plan.

## 1. Components/layers involved

| Layer | Responsibility |
|---|---|
| Frontend | Extend the existing event-input template (`Code/templates/event_in_a_box/event.html`) with an Anlassart select and a persönliche-Präferenzen multi-select (checkboxes, max 4 options). Extend the suggestions template to show a no-results message distinct from the "no recipe fits the budget" WS message. |
| API / Backend | Extend `EventInputForm` (`Code/event_in_a_box/forms.py`) with optional `event_type` and `preferences` fields. `views.event_input` and `views.suggestions` gain the filtering behavior; no new routes are required. |
| Application / Domain Logic | Add `Recipe.matches_classification(request)` to `event_in_a_box/domain.py` (framework-free, per CLAUDE.md's OOD rules — no Django import). Replace/extend `services.find_recipe_suggestions` filtering logic so eligibility is `matches_classification(request)`, decoupled from the WS 70%-of-budget cap (see §6). |
| Domain Model | See `data-model.md`. `PlanningRequest`, `Recipe` gain new fields; `EventType`, `Preference`, `PreferenceCategory` are introduced into `domain.py`. |
| Data Source | See §5 (mock-data strategy — **open decision**). |
| Backend Response | Unchanged shape: server-rendered HTML, Post/Redirect/Get. |
| Frontend Result | Suggestions page lists all eligible recipes (no price/selection UI yet — introduced by `003`). |

## 2. Data flow

```text
User (event.html form: budget, guests, Anlassart?, Präferenzen[0..4])
  -> POST / -> EventInputForm.is_valid()
  -> PlanningSession.start(guest_count, maximum_budget, event_type, preferences)
  -> GET /suggestions/
  -> repository.get_all() -> [Recipe, ...]
  -> filter: recipe.matches_classification(planning_request)
  -> render suggestions.html with eligible recipes (or no-match message)
```

## 3. Domain logic responsibilities

`Recipe.matches_classification(request: PlanningRequest) -> bool`, in `domain.py`:

```text
(request.event_type is None or request.event_type in recipe.supported_event_types)
AND all(pref in recipe.preferences for pref in request.selected_preferences)
```

This mirrors the canonical model's `Recipe.matchesClassification(request)` and the `findSuggestions`
predicate in the domain-model spec §5 (event-type/preference clauses only — the budget clause
there is superseded per CLAUDE.md's own precedence text, see §6 below).

Keep this pure and Django-free, consistent with `CLAUDE.md`'s "Object-oriented design rules"
(business calculations independent from HTTP/templates/DB frameworks).

## 4. Frontend/backend responsibilities

- Backend: validation (existing `EventInputForm` rules extended), filtering, session state.
- Frontend: present Anlassart as a single-select with an explicit "no preference" default option
  (`spec.md` §4: "the default value represents no specified Anlassart"); present preferences as a
  bounded multi-select (0–4). Enforce the 4-preference cap in the form (`forms.py`), not just the UI.

## 5. Mock-data strategy — **open decision, not silently resolved**

The Working Skeleton stores recipes as in-memory dataclasses in `mock_data.py`
(`MockRecipeRepository`/`MockProductRepository`). Separately, `models.py` / `admin.py` /
`migrations/0001_initial.py` already define and register Django ORM tables for `Recipe`, `Product`,
`Ingredient`, `EventType`, and `Preference` — built but **currently unused** by any view (per
`models.py`'s own docstring). CLAUDE.md's MVP scope lists "mock **or seeded** Transgourmet
products," and the ERM documents these as persisted tables, which suggests the ORM path was
intended to be wired in around the point event-type/preference filtering became necessary — i.e., now.

Two options, **neither silently chosen here**:

1. **Continue in-memory mock data**: add `event_type`/`preference` fields to the `domain.py`
   dataclasses and hand-write associations for each of the 3 WS mock recipes in `mock_data.py`.
   Simplest, smallest diff, keeps `models.py` dormant.
2. **Switch to DB-seeded data**: implement `DatabaseRecipeRepository`/`DatabaseProductRepository`
   (per the "Collaborating interfaces" section of the domain-model spec) reading through the
   existing Django ORM models, with `Recipe`/`Product`/`EventType`/`Preference`/`Ingredient` rows
   loaded via a data migration or a `manage.py` seed command. Uses the persistence layer that
   already exists for exactly this purpose; aligns with "seeded Transgourmet products" and with the
   integration-test guidance in `CLAUDE.md` ("recipe and product repositories" as an integration-test
   area).

<!-- TODO/DECISION (@EdiAnderegg): choose option 1 or 2 before implementing this feature. Both are
approved technology (Django ORM + PostgreSQL already in the stack); this is a mock-data-strategy
choice, not a new-technology introduction. Recommendation: option 2, since the ORM models, admin,
and migration already exist seemingly for this purpose and leaving them permanently dormant
contradicts their presence in the codebase — but this is a judgment call for the architecture
owner, not decided here. -->

Either way, `IRecipeRepository`/`IProductRepository` stay the seam (`repositories.py`); views and
`domain.py` do not change based on which option is chosen.

## 6. Interfaces/contracts required

No new HTTP/JSON contract. Page routes are unchanged (`POST /`, `GET /suggestions/`); no
`contracts/` directory is created for this feature per `CLAUDE.md` ("create contracts only where an
actual interface boundary exists").

**Resolved (@razec3, 2026-08-23, issue #8):** `002` alone removes the Working Skeleton's
`find_recipe_suggestions` 70%-of-budget suggestion cap (`001-working-skeleton/plan.md` §6). `spec.md`
§2 now explicitly identifies this as superseding Working Skeleton behavior, per `CLAUDE.md`'s
specification-precedence section. The cap does not apply from `002` onward; it does not linger
until `003` lands. Implement `Recipe.matches_classification`/`find_recipe_suggestions` filtering
with no budget-based eligibility check.

## 7. Testing approach

- Unit: `Recipe.matches_classification` — no Anlassart/no preferences (all eligible), Anlassart-only
  match/no-match, preference AND-combination, combined Anlassart+preferences.
- Integration: `EventInputForm` validation with the new optional fields; `views.suggestions`
  filtering against the (mock or seeded, per §5) repository.
- Acceptance (pytest-bdd): the 8 scenarios in `spec.md` §7, in a new
  `Code/tests/acceptance/features/event_configuration_and_filtering.feature`.

## 8. Implementation sequence

1. Resolve the §5 mock-data-strategy decision and the §6 budget-cap discrepancy (blocking).
2. Extend `domain.py`: `EventType`, `Preference`, `PreferenceCategory`, extend `PlanningRequest`
   and `Recipe`, add `matches_classification`.
3. Extend/seed data per the chosen §5 strategy.
4. Extend `EventInputForm` and `PlanningSession` (event type + preferences persisted alongside
   guest count/budget).
5. Extend `views.event_input` / `views.suggestions` and their templates.
6. Unit tests for `matches_classification`.
7. Integration tests for form validation and filtered suggestions.
8. Acceptance tests for `spec.md` §7 scenarios.
9. Update `Documentation/Testing/traceability.md` with the new scenario→test mapping.

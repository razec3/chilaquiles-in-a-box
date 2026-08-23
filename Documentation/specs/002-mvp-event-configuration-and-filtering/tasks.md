# Tasks: Event Configuration and Recipe Filtering

Derived from [`spec.md`](./spec.md), [`plan.md`](./plan.md), and [`data-model.md`](./data-model.md).
Ordered by dependency.

## Preparation (blocking — human decisions)

- [x] Get @razec3 decision on the Anlassart predefined values (`data-model.md` §3 TODO).
      **Resolved:** Business-Apéro, Vereinsanlass, Brunch (issue #12, 2026-08-23).
- [x] Get @razec3/@EdiAnderegg confirmation of the preference→`PreferenceCategory` mapping
      (`data-model.md` §3 TODO). **Resolved:** mapping approved as proposed (issue #12,
      2026-08-23).
- [x] Get @EdiAnderegg decision on mock-data strategy: in-memory vs. DB-seeded (`plan.md` §5).
      **Resolved:** DB-seeded (issue #12, 2026-08-23).
- [x] Get @razec3 decision on whether the Working Skeleton's 70%-of-budget suggestion cap is
      removed as of this feature or still applies until `003` lands (`plan.md` §6). **Resolved:**
      `002` alone removes the cap (issue #8, 2026-08-23).

## Domain layer

- [x] Add `EventType`, `Preference`, `PreferenceCategory` to `event_in_a_box/domain.py`.
- [x] Extend `PlanningRequest` with `event_type: EventType | None` and
      `selected_preferences: tuple[Preference, ...]`.
- [x] Extend `Recipe` with `supported_event_types: tuple[EventType, ...]` and
      `preferences: tuple[Preference, ...]`.
- [x] Implement `Recipe.matches_classification(request: PlanningRequest) -> bool`.
- [x] Unit tests: no filters (all eligible); Anlassart match/no-match; single preference
      match/no-match; combined Anlassart + multiple preferences (AND semantics); recipe missing one
      of several selected preferences is excluded. (`tests/unit/test_recipe_classification.py`.)

## Data layer

- [x] Seed mechanism for the DB-seeded strategy: data migration
      `migrations/0002_seed_reference_and_recipe_data.py` seeds the 3 `EventType`, 4
      `Preference`, and 3 recipe (with products/ingredients) rows. Covered by
      `tests/integration/test_seed_data.py`.
- [x] Implement `DatabaseRecipeRepository`/`DatabaseProductRepository` (`repositories.py`) and the
      mapping functions between the Django ORM models and the `domain.py` dataclasses. Also added
      `DatabaseEventTypeRepository`/`DatabasePreferenceRepository` (needed by `PlanningSession` to
      resolve session-stored codes back into domain dataclasses) and, via
      `migrations/0003_recipe_slug.py`, a `Recipe.slug` field so `domain.Recipe.id` and recipe URLs
      stay stable now that recipes are DB rows rather than mock objects — see `data-model.md`'s
      implementation addendum.
- [x] Confirm the seeded dataset includes recipes exercising every filter combination in
      `spec.md` §7: different Anlassart (`Business-Apéro` vs. `Vereinsanlass` vs. `Brunch`, the
      last with zero recipes — covers Scenario 5's "no matching recipe" case), at least one
      `Vegetarisch` recipe (`Mediterraner Pasta-Abend`), and a recipe matching both `Vegetarisch`
      and `Saisonal` (`Mediterraner Pasta-Abend`).

## Application layer

- [x] Extend `EventInputForm` with optional Anlassart (choice field) and preferences
      (multi-select, max 4) fields, using the approved predefined values.
- [x] Extend `PlanningSession` to persist `event_type`/`selected_preferences` alongside existing
      state, and to reset all downstream state when any event input changes (`spec.md` §7
      Scenario 8) — reuse/extend the existing `.start()`/`.clear()` methods.
- [x] Update `services.find_recipe_suggestions` (or its replacement) to filter via
      `matches_classification` only, removing the 70%-of-budget suggestion cap (`plan.md` §6).

## Views/templates

- [x] Update `event.html` with Anlassart select + preferences multi-select.
- [x] Update `suggestions.html` to render all eligible recipes and a distinct "no matching recipe"
      message with a way to return to event configuration.

## Tests

- [x] Integration tests: form validation for the new fields; `views.suggestions` filtering
      end-to-end against the chosen repository.
      (`tests/integration/test_event_configuration_and_filtering_views.py`.)
- [x] Acceptance tests: `Code/tests/acceptance/features/event_configuration_and_filtering.feature`
      covering `spec.md` §7 Scenarios 1–8.
- [x] Update `Documentation/Testing/traceability.md`.

## Validation

- [x] Run the full test suite (`docker compose run --rm web pytest`) — 74 passed.
- [x] Functional walkthrough of the extended event-input and suggestions pages against the real
      running stack (`docker compose up`, verified through nginx on `:8080` via HTTP requests):
      Anlassart select and preferences checkboxes render with the seeded choices; filtering by
      Anlassart/preferences and the distinct no-match message all behave as specified. No
      real-browser/visual smartphone-viewport check was performed — this environment has no
      browser automation tool available (`chromium-cli` not present). If a visual check at a
      smartphone viewport is required, someone with a browser should do a quick manual pass before
      considering the UI polish done.

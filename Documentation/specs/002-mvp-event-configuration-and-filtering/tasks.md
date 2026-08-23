# Tasks: Event Configuration and Recipe Filtering

Derived from [`spec.md`](./spec.md), [`plan.md`](./plan.md), and [`data-model.md`](./data-model.md).
Ordered by dependency.

## Preparation (blocking — human decisions)

- [ ] Get @razec3 decision on the Anlassart predefined values (`data-model.md` §3 TODO).
- [ ] Get @razec3/@EdiAnderegg confirmation of the preference→`PreferenceCategory` mapping
      (`data-model.md` §3 TODO).
- [ ] Get @EdiAnderegg decision on mock-data strategy: in-memory vs. DB-seeded (`plan.md` §5).
- [ ] Get @razec3 decision on whether the Working Skeleton's 70%-of-budget suggestion cap is
      removed as of this feature or still applies until `003` lands (`plan.md` §6).

## Domain layer

- [ ] Add `EventType`, `Preference`, `PreferenceCategory` to `event_in_a_box/domain.py`.
- [ ] Extend `PlanningRequest` with `event_type: EventType | None` and
      `selected_preferences: tuple[Preference, ...]`.
- [ ] Extend `Recipe` with `supported_event_types: tuple[EventType, ...]` and
      `preferences: tuple[Preference, ...]`.
- [ ] Implement `Recipe.matches_classification(request: PlanningRequest) -> bool`.
- [ ] Unit tests: no filters (all eligible); Anlassart match/no-match; single preference
      match/no-match; combined Anlassart + multiple preferences (AND semantics); recipe missing one
      of several selected preferences is excluded.

## Data layer

- [ ] Implement the mock-data strategy chosen in Preparation:
  - If in-memory: add event-type/preference tuples to each `Recipe` in `mock_data.py`.
  - If DB-seeded: implement `DatabaseRecipeRepository`/`DatabaseProductRepository`
    (`repositories.py`), a seed mechanism (data migration or `manage.py` command) for
    `EventType`/`Preference`/`Recipe`/`Product`/`Ingredient`, and mapping functions between the
    Django ORM models and the `domain.py` dataclasses.
- [ ] Confirm the seeded/mock dataset includes recipes exercising every filter combination in
      `spec.md` §7 (at least: recipes with different Anlassart, at least one `Vegetarisch` recipe,
      at least one recipe matching both `Vegetarisch` and `Saisonal`, and a filter combination with
      zero matches for Scenario 5).

## Application layer

- [ ] Extend `EventInputForm` with optional Anlassart (choice field) and preferences
      (multi-select, max 4) fields, using the approved predefined values.
- [ ] Extend `PlanningSession` to persist `event_type`/`selected_preferences` alongside existing
      state, and to reset all downstream state when any event input changes (`spec.md` §7
      Scenario 8) — reuse/extend the existing `.start()`/`.clear()` methods.
- [ ] Update `services.find_recipe_suggestions` (or its replacement) to filter via
      `matches_classification`, resolving the §6 budget-cap question from `plan.md`.

## Views/templates

- [ ] Update `event.html` with Anlassart select + preferences multi-select.
- [ ] Update `suggestions.html` to render all eligible recipes and a distinct "no matching recipe"
      message with a way to return to event configuration.

## Tests

- [ ] Integration tests: form validation for the new fields; `views.suggestions` filtering
      end-to-end against the chosen repository.
- [ ] Acceptance tests: `Code/tests/acceptance/features/event_configuration_and_filtering.feature`
      covering `spec.md` §7 Scenarios 1–8.
- [ ] Update `Documentation/Testing/traceability.md`.

## Validation

- [ ] Run the full test suite (`docker compose run --rm web pytest`).
- [ ] Manual smartphone-width walkthrough of the extended event-input and suggestions pages.

# Data Model: Event Configuration and Recipe Filtering

This file documents only the subset of the authoritative class model
([`Documentation/Architecture/event-in-a-box-domain-model-and-erm.md`](../../Architecture/event-in-a-box-domain-model-and-erm.md))
needed by this feature. It does not redefine the domain model. Compare to
[`001-working-skeleton/data-model.md`](../001-working-skeleton/data-model.md), which this feature extends.

## 1. Classes used

| Canonical class | Used here | Notes |
|---|---|---|
| `PlanningRequest` | Yes, extended | Working Skeleton used only `guestCount`/`maximumBudget`. This feature adds `eventType` (0..1) and `selectedPreferences` (0..4). |
| `Recipe` | Yes, extended | Working Skeleton used only `id`, `name`, `description`, `ingredients`. This feature adds `supportedEventTypes`, `preferences`, and `matchesClassification(request)`. |
| `EventType` | Yes, new | `code`, `displayName`. Maps to the German UI term **Anlassart**. |
| `Preference` | Yes, new | `code`, `displayName`, `category`. Maps to the German UI term **persönliche Präferenz**. |
| `PreferenceCategory` | Yes, new | Enumeration grouping preferences (`DIET`, `ORIGIN`, `SEASONALITY`, `CERTIFICATION`). |
| `Ingredient`, `Product` | Unchanged | Not filtered by this feature; carried through unchanged from the Working Skeleton subset. |

`AperoPackageCalculator` is **not** exercised for filtering. Filtering is a pure `Recipe.matchesClassification(request)` predicate; no cost calculation is required to determine eligibility (`spec.md` §5: "The system does not rank matching recipes").

## 2. Relationships/cardinalities used

Per the authoritative model:

- `Recipe "0..*" --> "1..*" EventType` — a recipe supports one or more event types.
- `Recipe "0..*" --> "0..*" Preference` — a recipe carries zero or more preferences.
- `Preference --> "1" PreferenceCategory`.

`spec.md` §6 restates this as "a recipe may be associated with multiple Anlassarten" / "multiple persönliche Präferenzen," which is consistent with the model's cardinalities.

## 3. Terminology mapping (German UI ↔ canonical class model)

| `spec.md` term | Canonical class/field |
|---|---|
| Anlassart | `EventType` (`PlanningRequest.eventType`, `Recipe.supportedEventTypes`) |
| Persönliche Präferenz | `Preference` (`PlanningRequest.selectedPreferences`, `Recipe.preferences`) |

**Approved (@razec3, 2026-08-23, issue #12):** the predefined Anlassart (EventType) values are
Business-Apéro (`BUSINESS_APERO`), Vereinsanlass (`VEREINSANLASS`), and Brunch (`BRUNCH`). See
`spec.md` §4.

**Approved (@razec3, 2026-08-23, issue #12):** the persönliche Präferenz -> `PreferenceCategory`
mapping is:

- Vegetarisch (`VEGETARISCH`) -> `DIET`
- Schweizer Produkt (`SCHWEIZER_PRODUKT`) -> `ORIGIN`
- Nachhaltige Packung (`NACHHALTIGE_PACKUNG`) -> `CERTIFICATION`
- Saisonal (`SAISONAL`) -> `SEASONALITY`

This differs from the example preference list in CLAUDE.md ("Vegan, Vegetarian, Regional,
Seasonal, Organic") — CLAUDE.md's list is explicitly non-exhaustive ("such as"), so this is not a
contradiction; the concrete MVP preference set above is the approved data.

## 4. Feature-specific constraints

- Every selected preference is a mandatory (AND) filter (CLAUDE.md business rule 12; `spec.md` §6).
- Anlassart, when specified, is a mandatory (hard) filter; when unspecified, it does not restrict eligibility (`spec.md` §6).
- A recipe is eligible only if it satisfies **all** active filters simultaneously (Anlassart AND every selected preference).
- Budget does **not** filter recipe eligibility in this feature (`spec.md` §6). This feature removes the Working Skeleton's 70%-of-budget suggestion cap outright (`spec.md` §2, decision recorded in issue #8); see `plan.md` §6.
- No ranking/recommendation logic — eligible recipes are returned unordered (or in a stable, arbitrary order).
- Changing any event-configuration input after recipe selection has started resets all downstream state (`spec.md` §6, Scenario 8) — this is session/application state, not part of the persisted domain model.

## 5. Persistence (ERM) impact

`Code/event_in_a_box/models.py` already defines `EventType`, `Preference`, and the `Recipe.supported_event_types` / `Recipe.preferences` `ManyToManyField`s, matching the ERM
(`Documentation/Architecture/event-in-a-box-domain-model-and-erm.md` §8) exactly. No schema
migration is required for this feature — the tables already exist (`0001_initial.py`). What is
missing is **seed data**: no `EventType`/`Preference` rows exist yet, and the Working Skeleton's
`mock_data.py` recipes carry no event-type/preference associations. See `plan.md` §5 for the
mock/seed-data decision this raises.

**Addendum (implementation, 2026-08-23):** implementing `DatabaseRecipeRepository` (the "Data
layer" task deferred by `plan.md` §5) surfaced one schema addition this data-model did not
anticipate: `Recipe` needed a stable, URL-safe identifier for `domain.Recipe.id`. The ERM's
`RECIPE.id` (`Documentation/Architecture/event-in-a-box-domain-model-and-erm.md` §8) is a
persistence-only primary key, not meant to leak into URLs — and the Working Skeleton's own tests
and templates already depend on the human-readable ids `mock_data.py` used (e.g.
`zuercher-geschnetzeltes`). `migrations/0003_recipe_slug.py` adds `Recipe.slug` (unique
`SlugField`) and backfills the three seeded recipes with their existing Working Skeleton ids, so no
URL or test behavior changes. See that migration's docstring for the full rationale.

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

<!-- TODO (spec.md line 52): the exact predefined Anlassart (EventType) values are not yet defined anywhere in the repository. Needs @razec3 product decision before EventType seed data can be written. -->

<!-- TODO: spec.md §4 lists four persönliche Präferenzen (Vegetarisch, Schweizer Produkt, Nachhaltige Packung, Saisonal). Their PreferenceCategory mapping is not defined anywhere. Proposed mapping, NOT approved — needs @EdiAnderegg/@razec3 confirmation:
  - Vegetarisch      -> DIET
  - Schweizer Produkt -> ORIGIN
  - Nachhaltige Packung -> CERTIFICATION
  - Saisonal          -> SEASONALITY
  This also differs from the example preference list in CLAUDE.md ("Vegan, Vegetarian, Regional, Seasonal, Organic") — CLAUDE.md's list is explicitly non-exhaustive ("such as"), so this is not a contradiction, but the concrete MVP preference set should be recorded as approved data, not inferred by a coding agent. -->

## 4. Feature-specific constraints

- Every selected preference is a mandatory (AND) filter (CLAUDE.md business rule 12; `spec.md` §6).
- Anlassart, when specified, is a mandatory (hard) filter; when unspecified, it does not restrict eligibility (`spec.md` §6).
- A recipe is eligible only if it satisfies **all** active filters simultaneously (Anlassart AND every selected preference).
- Budget does **not** filter recipe eligibility in this feature (`spec.md` §6). See `plan.md` §6 for the open question this raises about the Working Skeleton's 70%-of-budget suggestion cap.
- No ranking/recommendation logic — eligible recipes are returned unordered (or in a stable, arbitrary order).
- Changing any event-configuration input after recipe selection has started resets all downstream state (`spec.md` §6, Scenario 8) — this is session/application state, not part of the persisted domain model.

## 5. Persistence (ERM) impact

`Code/event_in_a_box/models.py` already defines `EventType`, `Preference`, and the `Recipe.supported_event_types` / `Recipe.preferences` `ManyToManyField`s, matching the ERM
(`Documentation/Architecture/event-in-a-box-domain-model-and-erm.md` §8) exactly. No schema
migration is required for this feature — the tables already exist (`0001_initial.py`). What is
missing is **seed data**: no `EventType`/`Preference` rows exist yet, and the Working Skeleton's
`mock_data.py` recipes carry no event-type/preference associations. See `plan.md` §5 for the
mock/seed-data decision this raises.

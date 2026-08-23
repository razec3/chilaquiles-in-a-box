# Quickstart: Event Configuration and Recipe Filtering

Builds on [`001-working-skeleton/quickstart.md`](../001-working-skeleton/quickstart.md); only the
delta is described here.

## Prerequisites

Same as the Working Skeleton. No new services, ports, or environment variables are introduced by
this feature. If the DB-seeded mock-data option is chosen (`plan.md` §5), an extra migration/seed
step is added below.

## Installation

```bash
cp .env.example .env
docker compose build
docker compose run --rm web python manage.py migrate
```

If DB-seeded mock data was chosen: also run the seed command/data migration once it exists (name
TBD — `<!-- TODO: fill in once the seed mechanism from plan.md §5 is implemented -->`).

## Start the application

```bash
docker compose up
```

Open [http://localhost:8080](http://localhost:8080).

## Verify the happy path

1. On the event input page, enter a valid budget and guest count, select an Anlassart, and select
   one or more persönliche Präferenzen (e.g. `Vegetarisch` and `Saisonal`).
2. Submit. The suggestions page shows only recipes that support the selected Anlassart **and**
   carry every selected preference (`spec.md` §7 Scenario 3).
3. Return to the event input page (without changing anything) and clear both optional filters,
   then resubmit. All available recipes are now eligible (`spec.md` §7 Scenario 4).
4. Select a combination of filters no recipe satisfies (e.g. an Anlassart/preference pair not
   present in the seed data). The suggestions page shows the no-match message and a way back to
   event configuration (`spec.md` §7 Scenario 5).
5. From the suggestions page, navigate back to event configuration and change the guest count.
   Confirm that any in-progress downstream state is discarded (`spec.md` §7 Scenario 8) —
   observable once `003`/`004` add recipe selection and an order draft; for this feature alone, it
   is enough that revisiting `/suggestions/` re-derives its list from the new inputs.

## Troubleshooting

If the suggestions page unexpectedly shows zero recipes for a combination expected to match, check
that the seed/mock dataset (`plan.md` §5) actually associates the relevant `EventType`/`Preference`
records with at least one recipe.

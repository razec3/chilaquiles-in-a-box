# Working Skeleton Quickstart

This file explains how another team member or judge can run the Working Skeleton locally.

Local execution is sufficient; deployment is not required.

## Prerequisites

- Docker and Docker Compose v2 (see the repository root [`README.md`](../../../README.md) for the full technical foundation setup).
- No additional runtimes are required beyond the technical foundation: the Working Skeleton adds no new services, environment variables, or ports.

## Installation

From the repository root:

```bash
cp .env.example .env
docker compose build
docker compose run --rm web python manage.py migrate
```

## Start the Application

```bash
docker compose up
```

Open [http://localhost:8080](http://localhost:8080) — this now shows the Working Skeleton's event input page directly.

## Verify the Happy Path

Use the example input from `spec.md`:

- Budget: CHF 1'000
- Number of guests: 50

Expected high-level result:

1. On the event input page, enter budget `1000` and guests `50`, then submit. One or more valid mock recipe proposals are displayed (every proposal's total price is at most CHF 700, i.e. 70% of the budget).
2. Selecting a proposal shows that recipe's ingredients, scaled to 50 guests.
3. Confirming the recipe shows the order draft: each required product, its number of packs, its line price, and the overall total.
4. Confirming the order draft shows a confirmation summary with a "Bestellung herunterladen" (download) action.
5. The download returns a JSON file matching [`contracts/order-draft.md`](./contracts/order-draft.md) — it lists article numbers, product names, package details, and pack counts, and contains no price fields.

To see the "no suitable recipe" case (`spec.md` Scenario 8), enter a very low budget (e.g. CHF 100) with 50 guests: no recipe stays within 70% of that budget, so the proposal page reports that no suitable recipe can be proposed.

## Troubleshooting

No known issues yet. If the proposal page unexpectedly shows no recipes for the example input above, check that `Code/event_in_a_box/mock_data.py` still defines recipes whose total cost is under CHF 700 for 50 guests.

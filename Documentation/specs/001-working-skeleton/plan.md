# Working Skeleton Implementation Plan

## 1. Purpose

This file describes how the Working Skeleton will be implemented technically.

The behavioral requirements are defined in [`spec.md`](./spec.md).

---

## 2. End-to-End Path

```text
User
  ↓
Frontend
  ↓
API / Backend
  ↓
Application / Domain Logic
  ↓
Data Source
  ↓
Backend Response
  ↓
Frontend Result
```

| Layer | Working Skeleton responsibility |
|---|---|
| Frontend | Django Templates render five server-rendered, mobile-first pages: event input, recipe suggestions, selected-recipe detail, order draft, and order confirmation. A small amount of unobtrusive vanilla JavaScript live-updates the purchase-limit hint on the event input page; no SPA framework is introduced. |
| API / Backend | Django views under `event_in_a_box` handle each page as a classic request/response (GET renders, POST processes and redirects — Post/Redirect/Get). There is no separate JSON API for the Working Skeleton; the only JSON response is the order-draft download. |
| Application / Domain Logic | `event_in_a_box/domain.py` holds `AperoPackageCalculator.calculate()` (scaling, package rounding, line cost, total cost, cost per guest — CLAUDE.md business rules 17-20). `event_in_a_box/services.py` holds `find_recipe_suggestions()`, the Working-Skeleton-specific 70%-of-budget suggestion filter (see §6 discrepancy note), and the session-backed `PlanningSession` helper that carries flow state between requests. |
| Domain Model | See [`data-model.md`](./data-model.md) for the exact subset of the canonical class model used here. |
| Data Source | `event_in_a_box/mock_data.py` defines three hard-coded `Recipe` instances (with their `Ingredient`/`Product` graphs) consistent with `data-model.md`. `MockRecipeRepository` and `MockProductRepository` in `event_in_a_box/repositories.py` expose this data through the same repository interfaces the full MVP will use, so a database-backed or Transgourmet-backed implementation can replace them later without changing views or domain logic. |
| Backend Response | Each page view returns a rendered `HttpResponse` (HTML). The download endpoint returns `application/json` with a `Content-Disposition: attachment` header, produced by `JsonProcurementOrderExporter`. |
| Frontend Result | Templates under `Code/templates/event_in_a_box/` render the proposal list, the selected recipe with scaled ingredients, the order draft (product, packs, line cost, total), and the confirmation screen with the download action, styled per §9. |

---

## 3. Technology Mapping

- Frontend: Django Templates (server-rendered HTML), plain CSS in `Code/static/css/app.css`, minimal vanilla JS in `Code/static/js/event-form.js`.
- Backend: Django views (function-based), following the existing `event_in_a_box` app conventions from the technical foundation.
- Data/mock-data mechanism: In-memory Python objects (`dataclasses`) constructed once in `event_in_a_box/mock_data.py` and served through repository classes. No database tables are introduced for recipes or products in the Working Skeleton (see §5 and the ERM's "temporary objects" note).
- Flow state between requests: the Django session (`django.contrib.sessions`, already part of the technical foundation) stores the entered `PlanningRequest` and the selected recipe id. Nothing is persisted to PostgreSQL.
- Serialization / JSON generation: `event_in_a_box/exporters.py::JsonProcurementOrderExporter`, using the standard library `json` module. No serialization framework is introduced.
- Local runtime: the existing Docker Compose stack (`web`, `db`, `nginx`) from the technical foundation. PostgreSQL continues to back only Django's own contrib tables; no Working Skeleton data is stored there.
- Testing tools: pytest, pytest-django, pytest-bdd (already in `Code/pyproject.toml`).

---

## 4. Domain-Model Usage

See [`data-model.md`](./data-model.md).

The Working Skeleton instantiates `PlanningRequest`, `Recipe`, `Ingredient`, `Product`, `ProductRequirement`, and `AperoPackage` from the canonical model in [`Documentation/Architecture/event-in-a-box-domain-model-and-erm.md`](../../Architecture/event-in-a-box-domain-model-and-erm.md). It does not instantiate `ProcurementOrderDraft`/`ProcurementOrderLine` as mutable, line-removable objects (stock removal is out of scope, per `spec.md` §3); instead `event_in_a_box/exporters.py` maps an `AperoPackage`'s `ProductRequirement`s directly into the exported JSON lines. `BudgetStatus` (`WITHIN_BUDGET`/`LIMIT_REACHED`/`OVER_BUDGET`) and the over-budget confirmation flow (business rules 21-23) are **not** implemented by the Working Skeleton; it uses the narrower 70%-of-budget cap defined in `spec.md` instead (see §6).

---

## 5. Mock-Data Approach

The Working Skeleton uses mock data rather than real dish recommendation logic or real product/pricing integration.

Three `Recipe` instances live in `event_in_a_box/mock_data.py`, each with its own `Ingredient` list referencing `Product` instances with a package quantity, measurement unit, sales-package type, and purchase price — consistent with `data-model.md` and the canonical `PRODUCT`/`INGREDIENT` shape. At a guest count of 50 and a budget of CHF 2'000, all three recipes stay within the 70%-of-budget cap (CHF 1'400), so every acceptance scenario in `spec.md` (including "no suitable recipe", exercised by raising the guest count or lowering the budget in a test) can be executed without editing the mock dataset.

The dataset is loaded once at import time (module-level constants); `MockRecipeRepository.get_all()` and `MockProductRepository.get_all()` / `get_by_article_number()` return it. No fixtures or database seeding are required.

---

## 6. Interfaces and Contracts

See [`contracts/order-draft.md`](./contracts/order-draft.md) for the downloadable JSON structure.

Request handling is plain Django view logic (form POST → redirect), so no separate request/response contract documents are needed beyond the JSON order-draft contract:

- Requesting recipe proposals: `POST /` (event input form) validates budget and guest count and redirects to `GET /suggestions/`.
- Selecting a recipe: `POST /suggestions/<recipe_id>/select/` redirects to `GET /recipes/<recipe_id>/`.
- Confirming the selected recipe / generating the order draft: `POST /recipes/<recipe_id>/confirm/` redirects to `GET /order/`.
- Confirming the order: `POST /order/confirm/` redirects to `GET /order/confirmation/`.
- Downloading the JSON order draft: `GET /order/download/`.

**Known discrepancy, flagged for Rodrigo/Eduard follow-up:** `spec.md` requires every suggested recipe's total price to be **≤ 70% of the entered budget**, while the project-wide business rule 14 in `CLAUDE.md` requires only **≤ 100% of the budget**, with `BudgetStatus` (`WITHIN_BUDGET`/`LIMIT_REACHED`/`OVER_BUDGET`) and an explicit over-budget confirmation for the full MVP. The Working Skeleton intentionally implements the stricter, simpler 70% rule only, as `spec.md` §3 explicitly places the rest of that business logic out of scope. The full MVP feature must decide whether the 70% cap survives as a permanent rule (e.g. reserved margin for drinks/staff) or was a Working-Skeleton-only simplification, and reconcile it with `BudgetStatus`.

---

## 7. Implementation Sequence

1. Domain layer: `domain.py` (dataclasses + `AperoPackageCalculator`), `mock_data.py`, `repositories.py`.
2. Application layer: `services.py` (`find_recipe_suggestions`, `PlanningSession`), `exporters.py` (`JsonProcurementOrderExporter`).
3. Views and URLs for the five pages plus the download endpoint.
4. Templates and static assets (base layout, five page templates, `app.css`, `event-form.js`), styled per §9.
5. Unit tests for the domain/application layer (scaling, rounding, aggregation, suggestion filtering, JSON export field set).
6. Integration tests for the view/session flow against PostgreSQL-backed Django (sessions are DB-backed via the `django_session` table, so this exercises the real database).
7. Acceptance tests (pytest-bdd) for the scenarios in `spec.md` §7.

This keeps the Working Skeleton vertically executable early: after step 3 the flow already works end-to-end with unstyled templates; step 4 applies the visual design on top without changing behavior.

---

## 8. Test Strategy

Each `spec.md` §7 scenario maps to at least a unit or integration test plus an acceptance
scenario. Unit tests avoid Django and PostgreSQL entirely (pure `domain.py`/`services.py`/
`exporters.py`); integration and acceptance tests use the Django test client against the real
PostgreSQL-backed session store, per the project's testing strategy.

The concrete scenario-to-test mapping is maintained once, in
[`Documentation/Testing/traceability.md`](../../Testing/traceability.md), rather than duplicated
here — see that file for exactly which test covers which scenario.

---

## 9. Visual Design

No approved Figma project link exists for the Working Skeleton yet (see [`Documentation/Design/figma.md`](../../Design/figma.md)). Screens were shared as reference screenshots (labelled *Event*, *Suggestion*, *Recipe*, *Order*, *Output*) showing a Transgourmet-branded, mobile-first, card-based layout: a white header with wordmark/search/cart icons, a grey breadcrumb bar, a bold page title, white rounded cards with a light shadow on a grey page background, and a full-width red primary call-to-action pinned near the bottom.

The Working Skeleton templates apply this visual language (colors, spacing, card and button styles) as the house style for all five pages. The exact screen-by-screen content of the reference screenshots was not reproduced literally where it conflicted with `spec.md`'s acceptance criteria (for example, the *Recipe* screenshot shows the same three recipe cards as the *Suggestion* screenshot, whereas `spec.md` Scenario 2 requires the *selected* recipe's own scaled ingredients to be displayed). This is a judgment call made to keep behavior traceable to `spec.md`; it should be confirmed against the real Figma file once one is linked in `figma.md`.

---

## 10. Local Execution

Deployment is not required for the Working Skeleton. Successful execution in the local development environment is sufficient.

See [`quickstart.md`](./quickstart.md) for the commands and prerequisites. No new ports or local
services are required beyond the technical foundation's existing `db`/`web`/`nginx` stack.

One environment variable was added while implementing this feature, not anticipated when this plan
was first written: `DJANGO_CSRF_TRUSTED_ORIGINS`. The app is only ever reached through the nginx
reverse proxy on `http://localhost:8080`, a different origin than Django's own host:port; without
this, Django's CSRF Origin check rejects every POST (form submissions only — this had no effect
before the Working Skeleton added the first HTML form). It defaults to `http://localhost:8080` in
`config/settings.py`, so no `.env` change is required for local development, but production
deployments on a different host must set it explicitly. See `.env.example` and the nginx `Host`
header fix in `Code/infrastructure/nginx/default.conf` (forwards `$http_host`, not `$host`, so
Django's own view of the request origin includes the port).

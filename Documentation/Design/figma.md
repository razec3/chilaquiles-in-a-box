# Figma Design Reference

Per `CLAUDE.md`, Figma is the source of truth for approved UI/UX design, and every implemented
screen must be traceable to an exact Figma page/frame link.

## Figma project

File: **UI-UX** (`zxox8notQy3Q7PV3d0xgTq`)

| Screen | Frame URL | Design status | Last review |
|---|---|---|---|
| Event | https://www.figma.com/design/zxox8notQy3Q7PV3d0xgTq/UI-UX?node-id=2006-8 | Draft | 2026-08-23 |
| Suggestion | https://www.figma.com/design/zxox8notQy3Q7PV3d0xgTq/UI-UX?node-id=2006-44 | Draft | 2026-08-23 |
| Recipe | https://www.figma.com/design/zxox8notQy3Q7PV3d0xgTq/UI-UX?node-id=2006-128 | Draft | 2026-08-23 |
| Order | https://www.figma.com/design/zxox8notQy3Q7PV3d0xgTq/UI-UX?node-id=2006-204 | Draft | 2026-08-23 |
| Output | https://www.figma.com/design/zxox8notQy3Q7PV3d0xgTq/UI-UX?node-id=2006-290 | Draft | 2026-08-23 |

Screen-to-frame mapping is by order (the five links were shared in this sequence, matching the
order the reference screenshots were shared in). **Not yet confirmed against the actual frame
names** — see "Access gap" below. Each maps to a Working Skeleton route:

| Screen | Route |
|---|---|
| Event | `GET/POST /` |
| Suggestion | `GET /suggestions/` |
| Recipe | `GET /recipes/<id>/` |
| Order | `GET /order/` |
| Output | `GET /order/confirmation/` |

Supported viewport/breakpoint: not confirmed from Figma directly (access gap below); implemented at
a single mobile width (~390px), matching the reference screenshots' phone-frame proportions. No
tablet/desktop layout exists yet.

## Access gap

Claude Code's Figma connection does not have access to this file (`get_metadata` /
`get_screenshot` both returned "you don't have edit access to this file. The file owner can share
it with you and make you an editor."; an unauthenticated fetch of the frame URL also returned
403). This means the exact frame names, layer structure, and pixel-level design (colors, spacing,
typography, the real Transgourmet logo asset) have **not** been pulled from Figma and verified
against the implementation — the five links above are recorded as-given, mapped to screens by
the order they were shared in, not confirmed by opening each frame.

To close this gap, either:
- share edit or view access to the file with the Figma account connected to Claude Code, or
- export the five frames (or paste screenshots, as before) so they can be compared directly.

## Known deviation (unresolved until the access gap is closed)

The originally shared *Recipe* reference screenshot showed the same three recipe cards as the
*Suggestion* screenshot (with "Details" instead of "Auswählen" buttons and no ingredient list).
`spec.md` Scenario 2 requires the *selected* recipe's own scaled ingredient list to be shown at
this step. The implementation follows `spec.md` — `/recipes/<id>/` shows the single selected
recipe with its scaled ingredients — rather than reproducing that screenshot literally. This
should be re-checked against the real `node-id=2006-128` frame once access is available.

## Other open items

- The Transgourmet logo/wordmark is currently a CSS/inline-SVG approximation in
  `Code/static/css/app.css`, not an exported asset from Figma.
- All five screens remain `Draft`. Set to `Approved` here once Rodrigo/Eduard have reviewed the
  live implementation against the actual Figma frames.

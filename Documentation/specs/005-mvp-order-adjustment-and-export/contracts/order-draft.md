# Contract: Order Draft JSON Export (v2)

Supersedes [`001-working-skeleton/contracts/order-draft.md`](../../001-working-skeleton/contracts/order-draft.md)
for this feature. This is a versioned export contract per `CLAUDE.md`; breaking field changes
require updating this document and the fixtures under `Code/tests/fixtures/`.

Produced by `JsonProcurementOrderExporter` and returned by the download endpoint as
`application/json` with a `Content-Disposition: attachment` header, per `spec.md` §6 "JSON export".

## What changed from v1 (`001`)

| v1 (`001-working-skeleton`) | v2 (this feature) | Why |
|---|---|---|
| `recipeName` (singular) | `recipeNames` (array) | `003` allows selecting multiple recipes; a single string can no longer represent the selection. |
| `lines[].orderedPackageCount` = the calculated value | `lines[].packageCount` = the **user-adjusted (active)** value | `spec.md` §6 "JSON export": "The JSON contains the actual number of packs to purchase" — the calculated value is a display-only reference, not exported. |
| All `productRequirements` included | Removed/inactive lines excluded entirely | `spec.md` §6: "Removed products are not included." |
| No price fields | No price fields (unchanged) | `spec.md` §6: "Price information is not included." Reconfirms v1's Scenario 5 rule. |

## Fields

| Field | Type | Description |
|---|---|---|
| `recipeNames` | array of string | Names of every currently selected recipe. |
| `guestCount` | integer | Number of guests the order draft was calculated for. |
| `lines` | array of line objects | One entry per **active** (not removed) product. |

Each entry in `lines`:

| Field | Type | Description |
|---|---|---|
| `articleNumber` | string | The product's unique Transgourmet article number. |
| `productName` | string | The product's display name. |
| `packageQuantity` | number | The package content amount, in `measuredIn` units. |
| `measuredIn` | string | One of `PIECE`, `GRAM`, `KILOGRAM`, `MILLILITRE`, `LITRE`. |
| `soldIn` | string | One of `TUBE`, `BOTTLE`, `BAG`, `BOX`, `CAN`, `PACKAGE`, `PIECE`. |
| `packageCount` | integer | The **active** (calculated, or user-adjusted if changed) number of packages to purchase. |

**Price information is deliberately not included** (`spec.md` §6, Scenario 8). The UI displays
prices; the exported JSON does not.

<!-- TODO: exact field names (`recipeNames` vs. e.g. `recipes`, `packageCount` vs. e.g.
`actualPackageCount`) are proposed here, not yet approved by @EdiAnderegg. Field names are safe to
change before any consumer exists; confirm before treating this as final. -->

<!-- TODO: this contract assumes JsonProcurementOrderExporter's signature changes from
`export(package: AperoPackage, guest_count: int)` (v1) to something that also carries the
adjustment/removal state (an adjusted ProcurementOrderDraft, per data-model.md §2's Option A, or
the AperoPackage plus an adjustments overlay, per Option B). The exact signature depends on which
option is chosen there. -->

## Example

For two selected recipes at 50 guests, with one line manually reduced to 1 pack and one line removed:

```json
{
  "recipeNames": ["Zürcher Geschnetzeltes mit Rösti", "Mediterraner Pasta-Abend"],
  "guestCount": 50,
  "lines": [
    {
      "articleNumber": "TG-10001",
      "productName": "Kalbsgeschnetzeltes",
      "packageQuantity": 1,
      "measuredIn": "KILOGRAM",
      "soldIn": "BAG",
      "packageCount": 1
    }
  ]
}
```

(A calculated line count of, say, 3 packs was manually reduced to 1; a second product that was
removed from the draft does not appear at all.)

## Field ordering

Field ordering is not consumer-significant (no downstream consumer exists yet, per v1); the
exporter uses the order shown above for readability.

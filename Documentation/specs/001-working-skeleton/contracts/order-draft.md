# Contract: Order Draft JSON Export

Produced by `JsonProcurementOrderExporter` (`Code/event_in_a_box/exporters.py`) and returned by
`GET /order/download/` as `application/json` with a `Content-Disposition: attachment` header.

This is a versioned export contract per `CLAUDE.md`. Breaking field changes require updating this
document and the fixtures under `Code/tests/fixtures/`.

## Fields

| Field | Type | Description |
|---|---|---|
| `recipeName` | string | Name of the confirmed recipe. |
| `guestCount` | integer | Number of guests the order draft was calculated for. |
| `lines` | array of line objects | One entry per required product. |

Each entry in `lines`:

| Field | Type | Description |
|---|---|---|
| `articleNumber` | string | The product's unique Transgourmet article number. |
| `productName` | string | The product's display name. |
| `packageQuantity` | number | The package content amount, in `measuredIn` units. |
| `measuredIn` | string | One of `PIECE`, `GRAM`, `KILOGRAM`, `MILLILITRE`, `LITRE`. |
| `soldIn` | string | One of `TUBE`, `BOTTLE`, `BAG`, `BOX`, `CAN`, `PACKAGE`, `PIECE`. |
| `orderedPackageCount` | integer | The rounded-up number of packages required (`ceiling(requiredQuantity / packageQuantity)`). |

**Price information is deliberately not included** (`spec.md` Scenario 5). The UI displays prices;
the exported JSON does not.

## Example

For the recipe "Zürcher Geschnetzeltes mit Rösti" at 50 guests:

```json
{
  "recipeName": "Zürcher Geschnetzeltes mit Rösti",
  "guestCount": 50,
  "lines": [
    {
      "articleNumber": "TG-10234",
      "productName": "Kalbsgeschnetzeltes",
      "packageQuantity": 1,
      "measuredIn": "KILOGRAM",
      "soldIn": "BAG",
      "orderedPackageCount": 10
    },
    {
      "articleNumber": "TG-10567",
      "productName": "Champignons",
      "packageQuantity": 1,
      "measuredIn": "KILOGRAM",
      "soldIn": "BOX",
      "orderedPackageCount": 3
    }
  ]
}
```

## Field ordering

Field ordering is not consumer-significant for the Working Skeleton (no downstream consumer exists
yet); the exporter uses the order shown above for readability.

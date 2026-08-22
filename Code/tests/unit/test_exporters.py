"""Unit tests for JsonProcurementOrderExporter against
Documentation/specs/001-working-skeleton/contracts/order-draft.md
(spec.md Scenario 5: no price fields in the downloaded JSON)."""

import json
from decimal import Decimal

import pytest

from event_in_a_box.domain import (
    AperoPackageCalculator,
    Ingredient,
    MeasurementUnit,
    PackageType,
    PlanningRequest,
    Product,
    Recipe,
)
from event_in_a_box.exporters import JsonProcurementOrderExporter

pytestmark = pytest.mark.unit


@pytest.fixture
def package():
    product = Product(
        article_number="TG-1",
        name="Kalbsgeschnetzeltes",
        package_quantity=Decimal("1"),
        measured_in=MeasurementUnit.KILOGRAM,
        sold_in=PackageType.BAG,
        purchase_price_per_package=Decimal("45.00"),
    )
    recipe = Recipe(
        id="recipe-1",
        name="Zürcher Geschnetzeltes",
        description="",
        ingredients=(Ingredient(product=product, quantity_per_guest=Decimal("0.2")),),
    )
    request = PlanningRequest(guest_count=50, maximum_budget=Decimal("2000"))
    return AperoPackageCalculator().calculate([recipe], request)


def test_export_contains_no_price_fields(package):
    document = JsonProcurementOrderExporter().export(package, guest_count=50)
    payload = json.loads(document.content)

    for line in payload["lines"]:
        assert "price" not in "".join(line.keys()).lower()
        assert set(line.keys()) == {
            "articleNumber",
            "productName",
            "packageQuantity",
            "measuredIn",
            "soldIn",
            "orderedPackageCount",
        }


def test_export_contains_expected_values(package):
    document = JsonProcurementOrderExporter().export(package, guest_count=50)
    payload = json.loads(document.content)

    assert payload["recipeName"] == "Zürcher Geschnetzeltes"
    assert payload["guestCount"] == 50
    (line,) = payload["lines"]
    assert line["articleNumber"] == "TG-1"
    assert line["productName"] == "Kalbsgeschnetzeltes"
    assert line["packageQuantity"] == 1.0
    assert line["measuredIn"] == "KILOGRAM"
    assert line["soldIn"] == "BAG"
    assert line["orderedPackageCount"] == 10


def test_export_document_metadata(package):
    document = JsonProcurementOrderExporter().export(package, guest_count=50)

    assert document.file_name == "order-draft.json"
    assert document.content_type == "application/json"

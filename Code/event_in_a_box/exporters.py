"""JSON procurement order-draft export.

Implements the contract in
Documentation/specs/001-working-skeleton/contracts/order-draft.md. Price
information is intentionally excluded (spec.md Scenario 5).
"""

import json
from dataclasses import dataclass

from .domain import AperoPackage


@dataclass(frozen=True)
class ExportDocument:
    file_name: str
    content_type: str
    content: bytes


class JsonProcurementOrderExporter:
    def export(self, package: AperoPackage, guest_count: int) -> ExportDocument:
        recipe_names = ", ".join(recipe.name for recipe in package.recipes)

        payload = {
            "recipeName": recipe_names,
            "guestCount": guest_count,
            "lines": [
                {
                    "articleNumber": requirement.product.article_number,
                    "productName": requirement.product.name,
                    "packageQuantity": float(requirement.product.package_quantity),
                    "measuredIn": requirement.product.measured_in.value,
                    "soldIn": requirement.product.sold_in.value,
                    "orderedPackageCount": requirement.required_package_count,
                }
                for requirement in package.product_requirements
            ],
        }

        content = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        return ExportDocument(
            file_name="order-draft.json",
            content_type="application/json",
            content=content,
        )

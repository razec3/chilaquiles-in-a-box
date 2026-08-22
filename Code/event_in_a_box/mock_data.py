"""Mock recipe/product data for the Working Skeleton.

See Documentation/specs/001-working-skeleton/plan.md §5. These three recipes
are consistent with the domain model and, at 50 guests, reproduce the
figures shown in the reference screenshots (CHF 1'100 / 900 / 1'250 total,
CHF 22 / 18 / 25 per guest) so the demo matches the design reference.
"""

from decimal import Decimal

from .domain import Ingredient, MeasurementUnit, PackageType, Product, Recipe


def _product(
    article_number: str,
    name: str,
    package_quantity: str,
    measured_in: MeasurementUnit,
    sold_in: PackageType,
    price: str,
) -> Product:
    return Product(
        article_number=article_number,
        name=name,
        package_quantity=Decimal(package_quantity),
        measured_in=measured_in,
        sold_in=sold_in,
        purchase_price_per_package=Decimal(price),
    )


def _ingredient(product: Product, quantity_per_guest: str) -> Ingredient:
    return Ingredient(product=product, quantity_per_guest=Decimal(quantity_per_guest))


_ZUERCHER_GESCHNETZELTES = Recipe(
    id="zuercher-geschnetzeltes",
    name="Zürcher Geschnetzeltes mit Rösti",
    description=(
        "Klassisches Schweizer Gericht mit Kalbfleisch, Champignons und knuspriger Rösti."
    ),
    ingredients=(
        _ingredient(
            _product(
                "TG-10001",
                "Kalbsgeschnetzeltes",
                "1",
                MeasurementUnit.KILOGRAM,
                PackageType.BAG,
                "45.00",
            ),
            "0.2",
        ),
        _ingredient(
            _product(
                "TG-10002", "Champignons", "1", MeasurementUnit.KILOGRAM, PackageType.BOX, "15.00"
            ),
            "0.06",
        ),
        _ingredient(
            _product(
                "TG-10003", "Rahm (Sahne)", "1", MeasurementUnit.LITRE, PackageType.BOTTLE, "12.00"
            ),
            "0.04",
        ),
        _ingredient(
            _product(
                "TG-10004", "Weisswein", "0.75", MeasurementUnit.LITRE, PackageType.BOTTLE, "15.00"
            ),
            "0.03",
        ),
        _ingredient(
            _product(
                "TG-10005", "Kartoffeln", "1", MeasurementUnit.KILOGRAM, PackageType.BAG, "2.50"
            ),
            "0.3",
        ),
        _ingredient(
            _product(
                "TG-10006", "Zwiebeln", "1", MeasurementUnit.KILOGRAM, PackageType.BAG, "4.00"
            ),
            "0.04",
        ),
        _ingredient(
            _product(
                "TG-10007", "Butter", "250", MeasurementUnit.GRAM, PackageType.PACKAGE, "2.75"
            ),
            "10",
        ),
        _ingredient(
            _product(
                "TG-10008",
                "Gewürze (Salz, Pfeffer, Paprika)",
                "1",
                MeasurementUnit.PIECE,
                PackageType.PACKAGE,
                "500.00",
            ),
            "0.02",
        ),
    ),
)

_MEDITERRANER_PASTA_ABEND = Recipe(
    id="mediterraner-pasta-abend",
    name="Mediterraner Pasta-Abend",
    description="Frische Pasta mit Tomatensauce, gegrilltem Gemüse und Parmigiano.",
    ingredients=(
        _ingredient(
            _product(
                "TG-20001",
                "Frische Pasta",
                "2.5",
                MeasurementUnit.KILOGRAM,
                PackageType.BAG,
                "24.00",
            ),
            "0.25",
        ),
        _ingredient(
            _product(
                "TG-20002", "Tomatensauce", "1", MeasurementUnit.LITRE, PackageType.CAN, "9.00"
            ),
            "0.2",
        ),
        _ingredient(
            _product(
                "TG-20003",
                "Gegrilltes Gemüse",
                "2.5",
                MeasurementUnit.KILOGRAM,
                PackageType.BAG,
                "22.00",
            ),
            "0.3",
        ),
        _ingredient(
            _product(
                "TG-20004", "Olivenöl", "1", MeasurementUnit.LITRE, PackageType.BOTTLE, "18.00"
            ),
            "0.1",
        ),
        _ingredient(
            _product(
                "TG-20005",
                "Parmigiano Reggiano",
                "1",
                MeasurementUnit.KILOGRAM,
                PackageType.PIECE,
                "38.00",
            ),
            "0.12",
        ),
        _ingredient(
            _product(
                "TG-20006",
                "Kräuter & Gewürze",
                "1",
                MeasurementUnit.PIECE,
                PackageType.PACKAGE,
                "240.00",
            ),
            "0.02",
        ),
    ),
)

_BBQ_GRILLPLATTE = Recipe(
    id="bbq-grillplatte",
    name="BBQ Grillplatte mit Beilagen",
    description="Gemischte Grillplatte mit Rindssteaks, Würsten, Maiskolben und Kartoffelsalat.",
    ingredients=(
        _ingredient(
            _product(
                "TG-30001", "Rindssteaks", "2.5", MeasurementUnit.KILOGRAM, PackageType.BAG, "60.00"
            ),
            "0.3",
        ),
        _ingredient(
            _product(
                "TG-30002",
                "Würste (Bratwurst/Cervelat Mix)",
                "2.5",
                MeasurementUnit.KILOGRAM,
                PackageType.BAG,
                "35.00",
            ),
            "0.25",
        ),
        _ingredient(
            _product(
                "TG-30003", "Maiskolben", "10", MeasurementUnit.PIECE, PackageType.BAG, "12.00"
            ),
            "1",
        ),
        _ingredient(
            _product(
                "TG-30004",
                "Kartoffelsalat",
                "2.5",
                MeasurementUnit.KILOGRAM,
                PackageType.BOX,
                "25.00",
            ),
            "0.25",
        ),
        _ingredient(
            _product(
                "TG-30005",
                "Grillsauce (BBQ)",
                "1",
                MeasurementUnit.LITRE,
                PackageType.BOTTLE,
                "14.00",
            ),
            "0.1",
        ),
        _ingredient(
            _product(
                "TG-30006",
                "Kräuterbutter",
                "1",
                MeasurementUnit.KILOGRAM,
                PackageType.PACKAGE,
                "16.00",
            ),
            "0.1",
        ),
        _ingredient(
            _product(
                "TG-30007",
                "Grillbedarf (Kohle, Anzünder)",
                "1",
                MeasurementUnit.PIECE,
                PackageType.PACKAGE,
                "380.00",
            ),
            "0.02",
        ),
    ),
)

MOCK_RECIPES: tuple[Recipe, ...] = (
    _ZUERCHER_GESCHNETZELTES,
    _MEDITERRANER_PASTA_ABEND,
    _BBQ_GRILLPLATTE,
)

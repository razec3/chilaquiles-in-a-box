"""Data migration seeding EventType/Preference reference data and the three
Working Skeleton recipes (mirrored from event_in_a_box/mock_data.py) into the
previously-dormant ORM tables.

Decision: Documentation/specs/002-mvp-event-configuration-and-filtering
(issue #12) — Anlassart values (Business-Apéro, Vereinsanlass, Brunch),
preference->category mapping, and DB-seeded mock-data strategy.

Recipe -> EventType/Preference associations are a reasoned classification,
not sourced from an approved product decision — see plan.md §5 for the
rationale (e.g. Mediterraner Pasta-Abend has no meat/fish ingredient, hence
Vegetarisch; BRUNCH intentionally has no recipe yet, covering spec.md §7
Scenario 5's "no matching recipe" case).
"""

from decimal import Decimal

from django.db import migrations

_PRODUCTS = [
    # (article_number, name, package_quantity, measured_in, sold_in, price)
    ("TG-10001", "Kalbsgeschnetzeltes", "1", "KILOGRAM", "BAG", "45.00"),
    ("TG-10002", "Champignons", "1", "KILOGRAM", "BOX", "15.00"),
    ("TG-10003", "Rahm (Sahne)", "1", "LITRE", "BOTTLE", "12.00"),
    ("TG-10004", "Weisswein", "0.75", "LITRE", "BOTTLE", "15.00"),
    ("TG-10005", "Kartoffeln", "1", "KILOGRAM", "BAG", "2.50"),
    ("TG-10006", "Zwiebeln", "1", "KILOGRAM", "BAG", "4.00"),
    ("TG-10007", "Butter", "250", "GRAM", "PACKAGE", "2.75"),
    ("TG-10008", "Gewürze (Salz, Pfeffer, Paprika)", "1", "PIECE", "PACKAGE", "500.00"),
    ("TG-20001", "Frische Pasta", "2.5", "KILOGRAM", "BAG", "24.00"),
    ("TG-20002", "Tomatensauce", "1", "LITRE", "CAN", "9.00"),
    ("TG-20003", "Gegrilltes Gemüse", "2.5", "KILOGRAM", "BAG", "22.00"),
    ("TG-20004", "Olivenöl", "1", "LITRE", "BOTTLE", "18.00"),
    ("TG-20005", "Parmigiano Reggiano", "1", "KILOGRAM", "PIECE", "38.00"),
    ("TG-20006", "Kräuter & Gewürze", "1", "PIECE", "PACKAGE", "240.00"),
    ("TG-30001", "Rindssteaks", "2.5", "KILOGRAM", "BAG", "60.00"),
    ("TG-30002", "Würste (Bratwurst/Cervelat Mix)", "2.5", "KILOGRAM", "BAG", "35.00"),
    ("TG-30003", "Maiskolben", "10", "PIECE", "BAG", "12.00"),
    ("TG-30004", "Kartoffelsalat", "2.5", "KILOGRAM", "BOX", "25.00"),
    ("TG-30005", "Grillsauce (BBQ)", "1", "LITRE", "BOTTLE", "14.00"),
    ("TG-30006", "Kräuterbutter", "1", "KILOGRAM", "PACKAGE", "16.00"),
    ("TG-30007", "Grillbedarf (Kohle, Anzünder)", "1", "PIECE", "PACKAGE", "380.00"),
]

_EVENT_TYPES = [
    ("BUSINESS_APERO", "Business-Apéro"),
    ("VEREINSANLASS", "Vereinsanlass"),
    ("BRUNCH", "Brunch"),
]

_PREFERENCES = [
    ("VEGETARISCH", "Vegetarisch", "DIET"),
    ("SCHWEIZER_PRODUKT", "Schweizer Produkt", "ORIGIN"),
    ("NACHHALTIGE_PACKUNG", "Nachhaltige Packung", "CERTIFICATION"),
    ("SAISONAL", "Saisonal", "SEASONALITY"),
]

_RECIPES = [
    {
        "name": "Zürcher Geschnetzeltes mit Rösti",
        "description": (
            "Klassisches Schweizer Gericht mit Kalbfleisch, Champignons und knuspriger Rösti."
        ),
        "event_types": ["BUSINESS_APERO", "VEREINSANLASS"],
        "preferences": ["SCHWEIZER_PRODUKT"],
        "ingredients": [
            ("TG-10001", "0.2"),
            ("TG-10002", "0.06"),
            ("TG-10003", "0.04"),
            ("TG-10004", "0.03"),
            ("TG-10005", "0.3"),
            ("TG-10006", "0.04"),
            ("TG-10007", "10"),
            ("TG-10008", "0.02"),
        ],
    },
    {
        "name": "Mediterraner Pasta-Abend",
        "description": "Frische Pasta mit Tomatensauce, gegrilltem Gemüse und Parmigiano.",
        "event_types": ["VEREINSANLASS"],
        "preferences": ["VEGETARISCH", "SAISONAL"],
        "ingredients": [
            ("TG-20001", "0.25"),
            ("TG-20002", "0.2"),
            ("TG-20003", "0.3"),
            ("TG-20004", "0.1"),
            ("TG-20005", "0.12"),
            ("TG-20006", "0.02"),
        ],
    },
    {
        "name": "BBQ Grillplatte mit Beilagen",
        "description": (
            "Gemischte Grillplatte mit Rindssteaks, Würsten, Maiskolben und Kartoffelsalat."
        ),
        "event_types": ["VEREINSANLASS"],
        "preferences": ["SAISONAL"],
        "ingredients": [
            ("TG-30001", "0.3"),
            ("TG-30002", "0.25"),
            ("TG-30003", "1"),
            ("TG-30004", "0.25"),
            ("TG-30005", "0.1"),
            ("TG-30006", "0.1"),
            ("TG-30007", "0.02"),
        ],
    },
]


def seed_reference_and_recipe_data(apps, schema_editor):
    EventType = apps.get_model("event_in_a_box", "EventType")
    Preference = apps.get_model("event_in_a_box", "Preference")
    Product = apps.get_model("event_in_a_box", "Product")
    Recipe = apps.get_model("event_in_a_box", "Recipe")
    Ingredient = apps.get_model("event_in_a_box", "Ingredient")

    event_types = {
        code: EventType.objects.create(code=code, display_name=display_name)
        for code, display_name in _EVENT_TYPES
    }
    preferences = {
        code: Preference.objects.create(code=code, display_name=display_name, category=category)
        for code, display_name, category in _PREFERENCES
    }
    products = {
        article_number: Product.objects.create(
            article_number=article_number,
            name=name,
            package_quantity=Decimal(package_quantity),
            measured_in=measured_in,
            sold_in=sold_in,
            purchase_price_per_package=Decimal(price),
        )
        for article_number, name, package_quantity, measured_in, sold_in, price in _PRODUCTS
    }

    for entry in _RECIPES:
        recipe = Recipe.objects.create(name=entry["name"], description=entry["description"])
        recipe.supported_event_types.set([event_types[code] for code in entry["event_types"]])
        recipe.preferences.set([preferences[code] for code in entry["preferences"]])
        for article_number, quantity_per_guest in entry["ingredients"]:
            Ingredient.objects.create(
                recipe=recipe,
                product=products[article_number],
                quantity_per_guest=Decimal(quantity_per_guest),
            )


def remove_seeded_reference_and_recipe_data(apps, schema_editor):
    EventType = apps.get_model("event_in_a_box", "EventType")
    Preference = apps.get_model("event_in_a_box", "Preference")
    Product = apps.get_model("event_in_a_box", "Product")
    Recipe = apps.get_model("event_in_a_box", "Recipe")

    # Deleting recipes first cascades their ingredients, freeing the
    # PROTECT'd products for deletion afterwards.
    Recipe.objects.filter(name__in=[entry["name"] for entry in _RECIPES]).delete()
    Product.objects.filter(article_number__in=[p[0] for p in _PRODUCTS]).delete()
    Preference.objects.filter(code__in=[p[0] for p in _PREFERENCES]).delete()
    EventType.objects.filter(code__in=[e[0] for e in _EVENT_TYPES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("event_in_a_box", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            seed_reference_and_recipe_data, remove_seeded_reference_and_recipe_data
        ),
    ]

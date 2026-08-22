"""Persisted master data — the tables in Documentation/Architecture's ERM:
RECIPE, PRODUCT, INGREDIENT, EVENT_TYPE, PREFERENCE, and their link tables
(implemented as ManyToManyField, which Django backs with its own join
tables). Standalone for now: the Working Skeleton's suggestion flow still
reads from event_in_a_box/mock_data.py, not these tables — see
Documentation/specs/001-working-skeleton/plan.md. These are distinct from
the framework-free dataclasses in event_in_a_box/domain.py.
"""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class MeasurementUnit(models.TextChoices):
    """Matches event_in_a_box.domain.MeasurementUnit's values."""

    PIECE = "PIECE", "Piece"
    GRAM = "GRAM", "Gram"
    KILOGRAM = "KILOGRAM", "Kilogram"
    MILLILITRE = "MILLILITRE", "Millilitre"
    LITRE = "LITRE", "Litre"


class PackageType(models.TextChoices):
    """Matches event_in_a_box.domain.PackageType's values."""

    TUBE = "TUBE", "Tube"
    BOTTLE = "BOTTLE", "Bottle"
    BAG = "BAG", "Bag"
    BOX = "BOX", "Box"
    CAN = "CAN", "Can"
    PACKAGE = "PACKAGE", "Package"
    PIECE = "PIECE", "Piece"


class Currency(models.TextChoices):
    """CLAUDE.md business rule 4: the MVP currency is CHF."""

    CHF = "CHF", "Swiss Franc"


class PreferenceCategory(models.TextChoices):
    DIET = "DIET", "Diet"
    ORIGIN = "ORIGIN", "Origin"
    SEASONALITY = "SEASONALITY", "Seasonality"
    CERTIFICATION = "CERTIFICATION", "Certification"


class Product(models.Model):
    """A Transgourmet article. CLAUDE.md business rules 6-8: unique article
    number, package quantity and purchase price greater than zero, exactly
    one measuredIn and one soldIn each."""

    article_number = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=200)
    package_quantity = models.DecimalField(
        max_digits=10, decimal_places=3, validators=[MinValueValidator(Decimal("0.001"))]
    )
    measured_in = models.CharField(max_length=20, choices=MeasurementUnit.choices)
    sold_in = models.CharField(max_length=20, choices=PackageType.choices)
    purchase_price_per_package = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.CHF)

    class Meta:
        ordering = ["article_number"]

    def __str__(self) -> str:
        return f"{self.article_number} – {self.name}"


class EventType(models.Model):
    code = models.CharField(max_length=32, primary_key=True)
    display_name = models.CharField(max_length=100)

    class Meta:
        ordering = ["display_name"]

    def __str__(self) -> str:
        return self.display_name


class Preference(models.Model):
    code = models.CharField(max_length=32, primary_key=True)
    display_name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=PreferenceCategory.choices)

    class Meta:
        ordering = ["category", "display_name"]

    def __str__(self) -> str:
        return self.display_name


class Recipe(models.Model):
    """CLAUDE.md business rule 5: a recipe must contain at least one
    ingredient — enforced in the admin via RecipeAdmin's inline
    (min_num=1), not at the model level (a recipe and its first ingredient
    cannot be created in a single row)."""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    supported_event_types = models.ManyToManyField(EventType, blank=True, related_name="recipes")
    preferences = models.ManyToManyField(Preference, blank=True, related_name="recipes")

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """One product requirement within a recipe. CLAUDE.md business rule 9:
    quantity_per_guest and the product's package_quantity share the
    product's measured_in unit (enforced by convention, not a constraint —
    there is only one quantity field here to hold it in)."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ingredients")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="ingredients")
    quantity_per_guest = models.DecimalField(
        max_digits=10, decimal_places=3, validators=[MinValueValidator(Decimal("0.001"))]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["recipe", "product"], name="unique_recipe_product")
        ]
        ordering = ["recipe", "product"]

    def __str__(self) -> str:
        return f"{self.recipe.name} – {self.product.name}"

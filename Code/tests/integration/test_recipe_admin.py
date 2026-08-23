"""Integration tests for the Recipe/Ingredient/EventType/Preference models
and their Django admin registration. See test_product_admin.py for Product.
"""

from decimal import Decimal

import pytest
from django.contrib.admin.sites import site
from django.db import IntegrityError
from django.db.models import ProtectedError

from event_in_a_box.models import EventType, Ingredient, Preference, Product, Recipe

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def _product(article_number="TG-1"):
    return Product.objects.create(
        article_number=article_number,
        name="Kalbsgeschnetzeltes",
        package_quantity="1",
        measured_in="KILOGRAM",
        sold_in="BAG",
        purchase_price_per_package="45.00",
    )


@pytest.mark.parametrize("model", [Recipe, EventType, Preference])
def test_model_is_registered_in_admin(model):
    assert model in site._registry


def test_ingredient_is_editable_only_inline_within_recipe():
    # Ingredient has no standalone admin section by design: it is edited via
    # RecipeAdmin's IngredientInline, matching CLAUDE.md's "a recipe must
    # contain at least one ingredient" invariant (enforced by that inline's
    # min_num=1, which only applies in the parent Recipe's admin form).
    assert Ingredient not in site._registry
    assert Ingredient in [inline.model for inline in site._registry[Recipe].inlines]


def test_recipe_can_have_ingredients_event_types_and_preferences():
    recipe = Recipe.objects.create(name="Zürcher Geschnetzeltes mit Rösti", description="")
    product = _product()
    Ingredient.objects.create(recipe=recipe, product=product, quantity_per_guest="0.2")
    event_type = EventType.objects.create(code="APERO", display_name="Apéro")
    preference = Preference.objects.create(code="VEGAN", display_name="Vegan", category="DIET")
    recipe.supported_event_types.add(event_type)
    recipe.preferences.add(preference)

    assert recipe.ingredients.count() == 1
    assert recipe.ingredients.first().quantity_per_guest == Decimal("0.2")
    assert list(recipe.supported_event_types.all()) == [event_type]
    assert list(recipe.preferences.all()) == [preference]


def test_a_product_appears_at_most_once_per_recipe():
    recipe = Recipe.objects.create(name="Recipe", description="")
    product = _product()
    Ingredient.objects.create(recipe=recipe, product=product, quantity_per_guest="0.2")

    with pytest.raises(IntegrityError):
        Ingredient.objects.create(recipe=recipe, product=product, quantity_per_guest="0.5")


def test_deleting_a_recipe_deletes_its_ingredients():
    recipe = Recipe.objects.create(name="Recipe", description="")
    product = _product()
    Ingredient.objects.create(recipe=recipe, product=product, quantity_per_guest="0.2")

    recipe.delete()

    assert Ingredient.objects.filter(product=product).count() == 0


def test_a_product_referenced_by_an_ingredient_cannot_be_deleted():
    recipe = Recipe.objects.create(name="Recipe", description="")
    product = _product()
    Ingredient.objects.create(recipe=recipe, product=product, quantity_per_guest="0.2")

    with pytest.raises(ProtectedError):
        product.delete()

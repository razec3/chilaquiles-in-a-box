"""Integration tests for migration 0002's seeded EventType/Preference
reference data and the three DB-mirrored recipes. See
Documentation/specs/002-mvp-event-configuration-and-filtering/plan.md §5
(mock-data strategy decision, issue #12) for the rationale.
"""

import pytest

from event_in_a_box.models import EventType, Preference, Product, Recipe

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def test_seeds_the_three_approved_event_types():
    codes = set(EventType.objects.values_list("code", flat=True))

    assert codes == {"BUSINESS_APERO", "VEREINSANLASS", "BRUNCH"}


def test_seeds_the_four_approved_preferences_with_their_categories():
    categories = dict(Preference.objects.values_list("code", "category"))

    assert categories == {
        "VEGETARISCH": "DIET",
        "SCHWEIZER_PRODUKT": "ORIGIN",
        "NACHHALTIGE_PACKUNG": "CERTIFICATION",
        "SAISONAL": "SEASONALITY",
    }


def test_seeds_the_three_working_skeleton_recipes_with_ingredients():
    names = set(Recipe.objects.values_list("name", flat=True))

    assert names == {
        "Zürcher Geschnetzeltes mit Rösti",
        "Mediterraner Pasta-Abend",
        "BBQ Grillplatte mit Beilagen",
    }
    assert all(recipe.ingredients.exists() for recipe in Recipe.objects.all())


def test_seeds_products_matching_every_recipe_ingredient():
    assert Product.objects.count() == 21


def test_brunch_has_no_seeded_recipe_yet():
    brunch = EventType.objects.get(code="BRUNCH")

    assert brunch.recipes.count() == 0


def test_vereinsanlass_covers_every_seeded_recipe():
    vereinsanlass = EventType.objects.get(code="VEREINSANLASS")

    assert vereinsanlass.recipes.count() == 3


def test_exactly_one_seeded_recipe_is_vegetarisch_and_saisonal():
    matching = Recipe.objects.filter(preferences__code="VEGETARISCH").filter(
        preferences__code="SAISONAL"
    )

    assert list(matching.values_list("name", flat=True)) == ["Mediterraner Pasta-Abend"]

"""Adds Recipe.slug: a stable, human-readable identifier used as the domain
Recipe.id and in URLs, distinct from the ERM's numeric primary key.

Documentation/Architecture/event-in-a-box-domain-model-and-erm.md §8 models
RECIPE.id as the persistence key; it is not meant to appear in URLs. This
migration was needed once DatabaseRecipeRepository (002's "Data layer" task)
replaced MockRecipeRepository: the Working Skeleton's mock_data.py recipes
used slug-like string ids (e.g. "zuercher-geschnetzeltes") that existing
Working Skeleton tests and URLs depend on. The three seeded recipes
(migrations/0002) are backfilled with those exact slugs so no URL or test
behavior changes.
"""

from django.db import migrations, models

_SLUGS_BY_NAME = {
    "Zürcher Geschnetzeltes mit Rösti": "zuercher-geschnetzeltes",
    "Mediterraner Pasta-Abend": "mediterraner-pasta-abend",
    "BBQ Grillplatte mit Beilagen": "bbq-grillplatte",
}


def populate_recipe_slugs(apps, schema_editor):
    Recipe = apps.get_model("event_in_a_box", "Recipe")
    for name, slug in _SLUGS_BY_NAME.items():
        Recipe.objects.filter(name=name).update(slug=slug)


def clear_recipe_slugs(apps, schema_editor):
    Recipe = apps.get_model("event_in_a_box", "Recipe")
    Recipe.objects.update(slug="")


class Migration(migrations.Migration):

    dependencies = [
        ("event_in_a_box", "0002_seed_reference_and_recipe_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="slug",
            # db_index=False here: SlugField defaults to db_index=True, and
            # Django's auto-generated index name only depends on table/column,
            # not on uniqueness. Indexing here would collide with the unique
            # index the AlterField below creates once the column is populated.
            field=models.SlugField(max_length=220, default="", blank=True, db_index=False),
            preserve_default=False,
        ),
        migrations.RunPython(populate_recipe_slugs, clear_recipe_slugs),
        migrations.AlterField(
            model_name="recipe",
            name="slug",
            field=models.SlugField(max_length=220, unique=True),
        ),
    ]

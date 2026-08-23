"""Repository implementations reading through the Django ORM.

Mirrors the canonical IRecipeRepository/DatabaseRecipeRepository shape (see
CLAUDE.md "Object-oriented design rules"). Maps the persisted `models.py` ORM
rows into the framework-free dataclasses in `domain.py`, so views and
`services.py` never see Django ORM instances. See
Documentation/specs/002-mvp-event-configuration-and-filtering/plan.md §5
(mock-data strategy decision, issue #12) — this replaced the Working
Skeleton's in-memory MockRecipeRepository/MockProductRepository.
"""

from . import domain, models

_RECIPE_RELATED = ("ingredients__product", "supported_event_types", "preferences")


def _to_domain_event_type(event_type: models.EventType) -> domain.EventType:
    return domain.EventType(code=event_type.code, display_name=event_type.display_name)


def _to_domain_preference(preference: models.Preference) -> domain.Preference:
    return domain.Preference(
        code=preference.code,
        display_name=preference.display_name,
        category=domain.PreferenceCategory(preference.category),
    )


def _to_domain_product(product: models.Product) -> domain.Product:
    return domain.Product(
        article_number=product.article_number,
        name=product.name,
        package_quantity=product.package_quantity,
        measured_in=domain.MeasurementUnit(product.measured_in),
        sold_in=domain.PackageType(product.sold_in),
        purchase_price_per_package=product.purchase_price_per_package,
    )


def _to_domain_recipe(recipe: models.Recipe) -> domain.Recipe:
    return domain.Recipe(
        id=recipe.slug,
        name=recipe.name,
        description=recipe.description,
        ingredients=tuple(
            domain.Ingredient(
                product=_to_domain_product(ingredient.product),
                quantity_per_guest=ingredient.quantity_per_guest,
            )
            for ingredient in recipe.ingredients.all()
        ),
        supported_event_types=tuple(
            _to_domain_event_type(event_type) for event_type in recipe.supported_event_types.all()
        ),
        preferences=tuple(
            _to_domain_preference(preference) for preference in recipe.preferences.all()
        ),
    )


class DatabaseRecipeRepository:
    def get_all(self) -> tuple[domain.Recipe, ...]:
        queryset = models.Recipe.objects.prefetch_related(*_RECIPE_RELATED)
        return tuple(_to_domain_recipe(recipe) for recipe in queryset)

    def get_by_id(self, recipe_id: str) -> domain.Recipe | None:
        try:
            recipe = models.Recipe.objects.prefetch_related(*_RECIPE_RELATED).get(slug=recipe_id)
        except models.Recipe.DoesNotExist:
            return None
        return _to_domain_recipe(recipe)


class DatabaseProductRepository:
    def get_all(self) -> tuple[domain.Product, ...]:
        return tuple(_to_domain_product(product) for product in models.Product.objects.all())

    def get_by_article_number(self, article_number: str) -> domain.Product | None:
        try:
            product = models.Product.objects.get(article_number=article_number)
        except models.Product.DoesNotExist:
            return None
        return _to_domain_product(product)


class DatabaseEventTypeRepository:
    def get_all(self) -> tuple[domain.EventType, ...]:
        return tuple(_to_domain_event_type(e) for e in models.EventType.objects.all())

    def get_by_code(self, code: str) -> domain.EventType | None:
        try:
            event_type = models.EventType.objects.get(code=code)
        except models.EventType.DoesNotExist:
            return None
        return _to_domain_event_type(event_type)


class DatabasePreferenceRepository:
    def get_all(self) -> tuple[domain.Preference, ...]:
        return tuple(_to_domain_preference(p) for p in models.Preference.objects.all())

    def get_by_codes(self, codes: tuple[str, ...]) -> tuple[domain.Preference, ...]:
        preferences = models.Preference.objects.filter(code__in=codes)
        return tuple(_to_domain_preference(p) for p in preferences)

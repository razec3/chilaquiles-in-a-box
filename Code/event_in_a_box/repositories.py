"""Repository interfaces and mock implementations.

Mirrors the shape of the future IRecipeRepository/IProductRepository and their
DatabaseRecipeRepository/TransgourmetProductRepository implementations (see
CLAUDE.md "Object-oriented design rules"), so those can replace the mock
implementations later without changing views or domain logic.
"""

from .domain import Product, Recipe
from .mock_data import MOCK_RECIPES


class MockRecipeRepository:
    def get_all(self) -> tuple[Recipe, ...]:
        return MOCK_RECIPES

    def get_by_id(self, recipe_id: str) -> Recipe | None:
        for recipe in MOCK_RECIPES:
            if recipe.id == recipe_id:
                return recipe
        return None


class MockProductRepository:
    def get_all(self) -> tuple[Product, ...]:
        products: dict[str, Product] = {}
        for recipe in MOCK_RECIPES:
            for ingredient in recipe.ingredients:
                products[ingredient.product.article_number] = ingredient.product
        return tuple(products.values())

    def get_by_article_number(self, article_number: str) -> Product | None:
        for product in self.get_all():
            if product.article_number == article_number:
                return product
        return None

from django.contrib import admin

from .models import EventType, Ingredient, Preference, Product, Recipe


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "article_number",
        "name",
        "package_quantity",
        "measured_in",
        "sold_in",
        "purchase_price_per_package",
        "currency",
    )
    list_filter = ("measured_in", "sold_in", "currency")
    search_fields = ("article_number", "name")
    ordering = ("article_number",)


class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1
    min_num = 1
    autocomplete_fields = ["product"]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "description")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("supported_event_types", "preferences")
    inlines = [IngredientInline]


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "display_name")
    search_fields = ("code", "display_name")


@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
    list_display = ("code", "display_name", "category")
    list_filter = ("category",)
    search_fields = ("code", "display_name")

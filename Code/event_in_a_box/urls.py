from django.urls import path

from . import views

app_name = "event_in_a_box"

urlpatterns = [
    path("", views.event_input, name="event_input"),
    path("health/", views.health, name="health"),
    path("suggestions/", views.suggestions, name="suggestions"),
    path("suggestions/<str:recipe_id>/select/", views.select_recipe, name="select_recipe"),
    path("recipes/<str:recipe_id>/", views.recipe_detail, name="recipe_detail"),
    path("recipes/<str:recipe_id>/confirm/", views.confirm_recipe, name="confirm_recipe"),
    path("order/", views.order_review, name="order_review"),
    path("order/confirm/", views.confirm_order, name="confirm_order"),
    path("order/confirmation/", views.order_confirmation, name="order_confirmation"),
    path("order/download/", views.download_order, name="download_order"),
    path("restart/", views.restart, name="restart"),
]

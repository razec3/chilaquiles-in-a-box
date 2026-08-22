from django.urls import path

from . import views

app_name = "event_in_a_box"

urlpatterns = [
    path("", views.index, name="index"),
    path("health/", views.health, name="health"),
]

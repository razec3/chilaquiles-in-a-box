from django.urls import include, path

urlpatterns = [
    path("", include("event_in_a_box.urls")),
]

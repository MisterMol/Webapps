from django.urls import path

from . import views


app_name = "setupwizard"


urlpatterns = [
    path("", views.start, name="start"),
]

from django.urls import path

from . import views


app_name = "inventory"


urlpatterns = [
    path("", views.inventory_overview, name="overview"),
    path("kaart/", views.public_inventory_map, name="public_map"),
    path("mutatie/nieuw/", views.stock_movement_create, name="movement_create"),
]

from django.urls import path

from . import views


app_name = "recipes"


urlpatterns = [
    path("", views.recipe_list, name="list"),
    path("beschikbaarheid/", views.recipe_availability_overview, name="availability"),
    path("beheer/<int:item_id>/", views.recipe_manage, name="manage"),
    path("regel/<int:line_id>/aanpassen/", views.recipe_ingredient_update, name="update_line"),
    path("regel/<int:line_id>/verwijderen/", views.recipe_ingredient_delete, name="delete_line"),
]

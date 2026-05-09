from django.urls import path

from . import views


app_name = "items"


urlpatterns = [
    path("", views.public_item_list, name="public_list"),
    path("beheer/", views.dashboard_item_list, name="dashboard_list"),
    path("beheer/nieuw/", views.item_create, name="create"),
    path("beheer/nieuw/<str:item_type>/", views.item_create, name="create_typed"),
    path("beheer/<int:item_id>/aanpassen/", views.item_update, name="update"),
    path("<slug:slug>/", views.public_item_detail, name="public_detail"),
]

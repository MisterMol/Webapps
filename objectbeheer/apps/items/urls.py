from django.urls import path

from . import views


app_name = "items"


urlpatterns = [
    path("", views.public_item_list, name="public_list"),
    path("dashboard/", views.dashboard_item_list, name="dashboard_list"),
    path("<slug:slug>/", views.public_item_detail, name="public_detail"),
]

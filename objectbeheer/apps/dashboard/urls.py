from django.urls import path

from . import views


app_name = "dashboard"


urlpatterns = [
    path("", views.home, name="home"),
    path("beheer/", views.dashboard_home, name="dashboard_home"),
]

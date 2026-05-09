from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("", include(("apps.dashboard.urls", "public"), namespace="public")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("items/", include("apps.items.urls")),
    path("inventory/", include("apps.inventory.urls")),
    path("recipes/", include("apps.recipes.urls")),
    path("setup/", include("apps.setupwizard.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

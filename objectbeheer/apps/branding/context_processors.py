from .models import BrandingSettings


def branding(request):
    branding_settings = BrandingSettings.objects.select_related("company").first()

    return {
        "branding": branding_settings,
    }

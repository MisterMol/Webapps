from .models import CompanyProfile


def company(request):
    profile = CompanyProfile.objects.first()
    settings = None

    if profile:
        settings = getattr(profile, "settings", None)

    return {
        "company": profile,
        "company_settings": settings,
    }

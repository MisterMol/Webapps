from .models import CompanyProfile


def company(request):
    profile = CompanyProfile.objects.first()
    return {
        "company": profile,
    }

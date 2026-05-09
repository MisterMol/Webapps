from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.company.models import CompanyProfile, CompanySettings
from apps.branding.models import BrandingSettings
from .models import SetupState


def start(request):
    setup_state = SetupState.objects.first()

    if setup_state and setup_state.is_completed:
        return redirect("public:home")

    if request.method == "POST":
        company_name = request.POST.get("company_name", "Restaurant De Molen").strip()
        public_name = request.POST.get("public_name", company_name).strip()
        primary_color = request.POST.get("primary_color", "#111827").strip()
        accent_color = request.POST.get("accent_color", "#f59e0b").strip()

        company = CompanyProfile.objects.create(
            name=company_name,
            public_name=public_name,
            company_type="restaurant",
            email=request.POST.get("email", "").strip(),
            phone=request.POST.get("phone", "").strip(),
            address=request.POST.get("address", "").strip(),
        )

        CompanySettings.objects.create(
            company=company,
            enable_inventory=True,
            enable_recipes=True,
            enable_orders=False,
            enable_public_catalog=True,
            allow_negative_stock=True,
            require_stock_reason=True,
            default_vat_rate=9,
        )

        BrandingSettings.objects.create(
            company=company,
            primary_color=primary_color,
            accent_color=accent_color,
            background_color="#f5f5f5",
            text_color="#222222",
            card_color="#ffffff",
            public_title=public_name,
            font_family="Arial, sans-serif",
        )

        SetupState.objects.create(
            is_completed=True,
            completed_at=timezone.now(),
        )

        messages.success(request, "Restaurant setup is voltooid.")
        return redirect("public:home")

    return render(request, "setupwizard/start.html")

from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.branding.models import BrandingSettings
from apps.company.models import CompanyProfile, CompanySettings

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
            enable_prices=True,
            enable_item_images=True,
            enable_featured_items=True,
            allow_negative_stock=True,
            require_stock_reason=True,
            default_vat_rate=9,
            show_public_prices=True,
            show_public_categories=True,
            show_public_labels=True,
        )

        BrandingSettings.objects.create(
            company=company,
            primary_color=primary_color,
            accent_color=accent_color,
            background_color="#f8fafc",
            text_color="#172033",
            muted_text_color="#64748b",
            card_color="#ffffff",
            border_color="#e5e7eb",
            public_title=public_name,
            font_family="Inter, Arial, sans-serif",
            show_images_by_default=True,
            use_soft_shadows=True,
            rounded_corners=18,
            max_page_width=1180,
        )

        SetupState.objects.create(
            is_completed=True,
            completed_at=timezone.now(),
        )

        messages.success(request, "Restaurant setup is voltooid.")
        return redirect("public:home")

    return render(request, "setupwizard/start.html")

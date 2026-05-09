from django.contrib import admin

from .models import CompanyProfile, CompanySettings


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "public_name", "company_type", "email", "phone")
    search_fields = ("name", "public_name", "email")


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "enable_inventory",
        "enable_recipes",
        "enable_orders",
        "enable_public_catalog",
        "allow_negative_stock",
        "require_stock_reason",
        "default_vat_rate",
    )

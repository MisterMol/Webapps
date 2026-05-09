from django.contrib import admin

from .models import CompanyProfile, CompanySettings


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "public_name", "company_type", "email", "phone")
    list_filter = ("company_type",)
    search_fields = ("name", "public_name", "email", "phone")


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Modules",
            {
                "fields": (
                    "enable_inventory",
                    "enable_recipes",
                    "enable_orders",
                    "enable_public_catalog",
                    "enable_prices",
                    "enable_item_images",
                    "enable_featured_items",
                )
            },
        ),
        (
            "Voorraad",
            {
                "fields": (
                    "allow_negative_stock",
                    "require_stock_reason",
                )
            },
        ),
        (
            "Publieke weergave",
            {
                "fields": (
                    "show_public_prices",
                    "show_public_categories",
                    "show_public_labels",
                    "default_vat_rate",
                )
            },
        ),
    )

    list_display = (
        "company",
        "enable_inventory",
        "enable_recipes",
        "enable_orders",
        "enable_public_catalog",
        "enable_item_images",
        "show_public_prices",
    )

from django.contrib import admin

from .models import BrandingSettings


@admin.register(BrandingSettings)
class BrandingSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "primary_color",
        "accent_color",
        "background_color",
        "text_color",
        "card_color",
        "font_family",
    )

from django.contrib import admin

from .models import BrandingSettings


@admin.register(BrandingSettings)
class BrandingSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Merk",
            {
                "fields": (
                    "company",
                    "public_title",
                    "logo",
                    "default_item_image",
                )
            },
        ),
        (
            "Kleuren",
            {
                "fields": (
                    "primary_color",
                    "accent_color",
                    "background_color",
                    "text_color",
                    "muted_text_color",
                    "card_color",
                    "border_color",
                )
            },
        ),
        (
            "Layout",
            {
                "fields": (
                    "font_family",
                    "show_images_by_default",
                    "use_soft_shadows",
                    "rounded_corners",
                    "max_page_width",
                )
            },
        ),
    )

    list_display = (
        "company",
        "primary_color",
        "accent_color",
        "background_color",
        "show_images_by_default",
        "rounded_corners",
    )

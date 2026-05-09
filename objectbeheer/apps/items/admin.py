from django.contrib import admin

from .models import Allergen, Category, Item, ItemImage, Label


class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 1
    fields = ("image", "media_kind", "alt_text", "caption", "sort_order", "is_primary", "is_public")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "sort_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "color")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Allergen)
class AllergenAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Basis",
            {
                "fields": (
                    "item_type",
                    "name",
                    "slug",
                    "sku",
                    "category",
                    "labels",
                    "status",
                    "is_featured",
                )
            },
        ),
        (
            "Tekst",
            {
                "fields": (
                    "short_description",
                    "description",
                )
            },
        ),
        (
            "Voorraad en maten",
            {
                "fields": (
                    "unit",
                    "is_stock_tracked",
                    "minimum_stock",
                )
            },
        ),
        (
            "Prijs",
            {
                "fields": (
                    "sale_price",
                    "purchase_price",
                    "vat_rate",
                )
            },
        ),
        (
            "Media",
            {
                "fields": (
                    "show_image",
                    "use_default_image_when_missing",
                )
            },
        ),
        (
            "Archief",
            {
                "fields": (
                    "archived_at",
                    "archived_by",
                )
            },
        ),
    )

    list_display = (
        "name",
        "item_type",
        "category",
        "unit",
        "sale_price",
        "is_stock_tracked",
        "show_image",
        "status",
        "is_featured",
    )
    list_filter = (
        "item_type",
        "category",
        "status",
        "is_stock_tracked",
        "show_image",
        "is_featured",
    )
    search_fields = ("name", "sku", "short_description", "description")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("labels",)
    readonly_fields = ("archived_at", "archived_by")
    inlines = [ItemImageInline]


@admin.register(ItemImage)
class ItemImageAdmin(admin.ModelAdmin):
    list_display = ("item", "media_kind", "alt_text", "caption", "sort_order", "is_primary", "is_public", "uploaded_at")
    list_filter = ("media_kind", "is_primary", "is_public")
    search_fields = ("item__name", "alt_text", "caption")

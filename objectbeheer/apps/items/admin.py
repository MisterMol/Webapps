from django.contrib import admin

from .models import Category, Item, ItemImage, Label


class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "sort_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "item_type",
        "category",
        "unit",
        "sale_price",
        "is_stock_tracked",
        "status",
        "is_featured",
    )
    list_filter = ("item_type", "category", "status", "is_stock_tracked", "is_featured")
    search_fields = ("name", "sku", "description")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("labels",)
    inlines = [ItemImageInline]


@admin.register(ItemImage)
class ItemImageAdmin(admin.ModelAdmin):
    list_display = ("item", "alt_text", "sort_order", "is_primary", "uploaded_at")
    list_filter = ("is_primary",)
    search_fields = ("item__name", "alt_text")

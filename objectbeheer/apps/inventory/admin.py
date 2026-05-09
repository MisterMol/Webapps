from django.contrib import admin

from .models import StockLocation, StockMovement, Unit


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("name", "symbol", "unit_type", "decimal_places", "is_active")
    list_filter = ("unit_type", "is_active")
    search_fields = ("name", "symbol")


@admin.register(StockLocation)
class StockLocationAdmin(admin.ModelAdmin):
    list_display = ("name", "is_default", "is_active")
    list_filter = ("is_default", "is_active")
    search_fields = ("name", "description")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("item", "location", "movement_type", "quantity", "reason", "created_by", "created_at")
    list_filter = ("movement_type", "location", "created_at")
    search_fields = ("item__name", "reason", "note")
    readonly_fields = ("created_at",)

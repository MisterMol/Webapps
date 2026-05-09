from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "object_type", "object_id", "created_by", "created_at")
    list_filter = ("action", "object_type", "created_at")
    search_fields = ("action", "object_type", "object_id", "message")
    readonly_fields = ("action", "object_type", "object_id", "message", "old_value", "new_value", "created_by", "created_at")

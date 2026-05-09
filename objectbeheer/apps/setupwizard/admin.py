from django.contrib import admin

from .models import SetupState


@admin.register(SetupState)
class SetupStateAdmin(admin.ModelAdmin):
    list_display = ("is_completed", "completed_at")

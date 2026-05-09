from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    action = models.CharField(max_length=120)
    object_type = models.CharField(max_length=120, blank=True)
    object_id = models.CharField(max_length=80, blank=True)
    message = models.TextField(blank=True)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "auditlog"
        verbose_name_plural = "auditlogs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} op {self.created_at}"

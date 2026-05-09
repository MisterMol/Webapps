from django.db import models


class SetupState(models.Model):
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "setupstatus"
        verbose_name_plural = "setupstatus"

    def __str__(self):
        return "Setup voltooid" if self.is_completed else "Setup niet voltooid"

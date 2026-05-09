from django.db import models


class BrandingSettings(models.Model):
    company = models.OneToOneField(
        "company.CompanyProfile",
        on_delete=models.CASCADE,
        related_name="branding",
    )
    logo = models.ImageField(upload_to="branding/", blank=True)
    primary_color = models.CharField(max_length=7, default="#111827")
    accent_color = models.CharField(max_length=7, default="#f59e0b")
    background_color = models.CharField(max_length=7, default="#f5f5f5")
    text_color = models.CharField(max_length=7, default="#222222")
    card_color = models.CharField(max_length=7, default="#ffffff")
    public_title = models.CharField(max_length=160, blank=True)
    font_family = models.CharField(max_length=120, default="Arial, sans-serif")

    class Meta:
        verbose_name = "branding"
        verbose_name_plural = "branding"

    def __str__(self):
        return f"Branding voor {self.company}"

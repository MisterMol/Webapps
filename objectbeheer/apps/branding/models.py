from django.db import models


class BrandingSettings(models.Model):
    company = models.OneToOneField(
        "company.CompanyProfile",
        on_delete=models.CASCADE,
        related_name="branding",
    )

    logo = models.ImageField(upload_to="branding/", blank=True)
    default_item_image = models.ImageField(upload_to="branding/defaults/", blank=True)

    primary_color = models.CharField(max_length=7, default="#111827")
    accent_color = models.CharField(max_length=7, default="#f59e0b")
    background_color = models.CharField(max_length=7, default="#f8fafc")
    text_color = models.CharField(max_length=7, default="#172033")
    muted_text_color = models.CharField(max_length=7, default="#64748b")
    card_color = models.CharField(max_length=7, default="#ffffff")
    border_color = models.CharField(max_length=7, default="#e5e7eb")

    public_title = models.CharField(max_length=160, blank=True)
    font_family = models.CharField(
        max_length=120,
        default="Inter, Arial, sans-serif",
    )

    show_images_by_default = models.BooleanField(default=True)
    use_soft_shadows = models.BooleanField(default=True)
    rounded_corners = models.PositiveIntegerField(default=18)
    max_page_width = models.PositiveIntegerField(default=1180)

    class Meta:
        verbose_name = "branding"
        verbose_name_plural = "branding"

    def __str__(self):
        return f"Branding voor {self.company}"

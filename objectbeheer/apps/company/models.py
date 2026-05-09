from django.db import models


class CompanyProfile(models.Model):
    COMPANY_TYPES = [
        ("restaurant", "Restaurant"),
        ("retail", "Winkel"),
        ("storage", "Opslag"),
        ("real_estate", "Makelaar"),
        ("general", "Algemeen bedrijf"),
    ]

    name = models.CharField(max_length=160)
    public_name = models.CharField(max_length=160, blank=True)
    company_type = models.CharField(max_length=40, choices=COMPANY_TYPES, default="general")
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    website = models.URLField(blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "bedrijfsprofiel"
        verbose_name_plural = "bedrijfsprofielen"

    def __str__(self):
        return self.public_name or self.name


class CompanySettings(models.Model):
    company = models.OneToOneField(
        CompanyProfile,
        on_delete=models.CASCADE,
        related_name="settings",
    )

    enable_inventory = models.BooleanField(default=True)
    enable_recipes = models.BooleanField(default=True)
    enable_orders = models.BooleanField(default=False)
    enable_public_catalog = models.BooleanField(default=True)
    enable_prices = models.BooleanField(default=True)
    enable_item_images = models.BooleanField(default=True)
    enable_featured_items = models.BooleanField(default=True)

    allow_negative_stock = models.BooleanField(default=True)
    require_stock_reason = models.BooleanField(default=True)
    default_vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=9)

    show_public_prices = models.BooleanField(default=True)
    show_public_categories = models.BooleanField(default=True)
    show_public_labels = models.BooleanField(default=True)

    class Meta:
        verbose_name = "bedrijfsinstelling"
        verbose_name_plural = "bedrijfsinstellingen"

    def __str__(self):
        return f"Instellingen voor {self.company}"

    def module_enabled(self, module_code):
        mapping = {
            "inventory": self.enable_inventory,
            "recipes": self.enable_recipes,
            "orders": self.enable_orders,
            "public_catalog": self.enable_public_catalog,
            "prices": self.enable_prices,
            "item_images": self.enable_item_images,
            "featured_items": self.enable_featured_items,
        }

        return mapping.get(module_code, False)

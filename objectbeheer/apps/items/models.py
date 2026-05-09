from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "categorie"
        verbose_name_plural = "categorieën"
        ordering = ["sort_order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Label(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = "label"
        verbose_name_plural = "labels"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Item(models.Model):
    ITEM_TYPES = [
        ("ingredient", "Ingrediënt"),
        ("menu_item", "Menu-item"),
        ("product", "Product"),
        ("asset", "Bedrijfsmiddel"),
        ("property", "Woning of pand"),
        ("service", "Dienst"),
        ("storage_unit", "Opslagobject"),
    ]

    STATUS_CHOICES = [
        ("draft", "Concept"),
        ("active", "Actief"),
        ("inactive", "Inactief"),
        ("archived", "Gearchiveerd"),
    ]

    item_type = models.CharField(max_length=40, choices=ITEM_TYPES, default="product")
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    sku = models.CharField(max_length=80, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="items",
    )
    labels = models.ManyToManyField(Label, blank=True, related_name="items")
    description = models.TextField(blank=True)
    unit = models.ForeignKey(
        "inventory.Unit",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="items",
    )
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=9)
    minimum_stock = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    is_stock_tracked = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="active")
    archived_at = models.DateTimeField(null=True, blank=True)
    archived_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="archived_items",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "item"
        verbose_name_plural = "items"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 2

            while Item.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def primary_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()

    def __str__(self):
        return self.name


class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="items/")
    alt_text = models.CharField(max_length=160, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "itemafbeelding"
        verbose_name_plural = "itemafbeeldingen"
        ordering = ["sort_order", "id"]

    def save(self, *args, **kwargs):
        if self.is_primary:
            ItemImage.objects.filter(item=self.item, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Afbeelding voor {self.item.name}"

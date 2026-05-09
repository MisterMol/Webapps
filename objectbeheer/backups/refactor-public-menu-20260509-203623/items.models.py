from pathlib import Path

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
    description = models.CharField(max_length=220, blank=True)
    color = models.CharField(max_length=7, default="#e5e7eb")

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
        ("menu_item", "Gerecht of menu-item"),
        ("product", "Product"),
        ("drink", "Drank"),
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
    short_description = models.CharField(max_length=220, blank=True)

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

    show_image = models.BooleanField(default=True)
    use_default_image_when_missing = models.BooleanField(default=True)

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
        permissions = [
            ("can_manage_items", "Kan items beheren"),
        ]

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

    def primary_media(self):
        return self.media_files.filter(is_primary=True, is_public=True).first() or self.media_files.filter(is_public=True).first()

    def primary_image(self):
        return self.primary_media()

    def primary_thumbnail_url(self):
        media = self.primary_media()

        if not media:
            return ""

        thumb_path = Path("media") / "items" / "thumbs" / f"{self.slug}-{media.id}.webp"

        if not thumb_path.exists():
            return media.image.url

        return f"/media/items/thumbs/{self.slug}-{media.id}.webp"

    def display_description(self):
        return self.short_description or self.description

    def should_show_image(self, company_settings=None, branding=None):
        if company_settings and not company_settings.enable_item_images:
            return False

        if branding and not branding.show_images_by_default:
            return False

        return self.show_image

    def __str__(self):
        return self.name


class ItemImage(models.Model):
    MEDIA_KINDS = [
        ("image", "Afbeelding"),
        ("gif", "Gif"),
        ("video", "Video"),
        ("other", "Overig"),
    ]

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="media_files")
    image = models.FileField(upload_to="items/media/")
    media_kind = models.CharField(max_length=20, choices=MEDIA_KINDS, default="image")
    alt_text = models.CharField(max_length=160, blank=True)
    caption = models.CharField(max_length=220, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "itemmedia"
        verbose_name_plural = "itemmedia"
        ordering = ["sort_order", "id"]

    def save(self, *args, **kwargs):
        if not self.media_kind:
            self.media_kind = self.detect_media_kind()

        if self.is_primary:
            ItemImage.objects.filter(item=self.item, is_primary=True).exclude(pk=self.pk).update(is_primary=False)

        super().save(*args, **kwargs)

    def detect_media_kind(self):
        suffix = Path(self.image.name).suffix.lower()

        if suffix in [".jpg", ".jpeg", ".png", ".webp", ".avif", ".svg"]:
            return "image"

        if suffix == ".gif":
            return "gif"

        if suffix in [".mp4", ".webm", ".mov"]:
            return "video"

        return "other"

    @property
    def is_video(self):
        return self.media_kind == "video"

    @property
    def is_visual(self):
        return self.media_kind in ["image", "gif", "video"]

    def __str__(self):
        return f"Media voor {self.item.name}"

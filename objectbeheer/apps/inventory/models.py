from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum


class Unit(models.Model):
    UNIT_TYPES = [
        ("piece", "Stuks"),
        ("weight", "Gewicht"),
        ("volume", "Volume"),
        ("length", "Lengte"),
        ("package", "Verpakking"),
    ]

    name = models.CharField(max_length=80, unique=True)
    symbol = models.CharField(max_length=20, unique=True)
    unit_type = models.CharField(max_length=30, choices=UNIT_TYPES, default="piece")
    decimal_places = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "eenheid"
        verbose_name_plural = "eenheden"
        ordering = ["unit_type", "name"]

    def __str__(self):
        return self.symbol


class StockLocation(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "voorraadlocatie"
        verbose_name_plural = "voorraadlocaties"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if self.is_default:
            StockLocation.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ("in", "Voorraad erbij"),
        ("out", "Voorraad eraf"),
        ("correction", "Correctie"),
        ("waste", "Verspilling"),
        ("sale", "Verkoop"),
        ("purchase", "Inkoop"),
        ("recipe_use", "Receptverbruik"),
    ]

    item = models.ForeignKey("items.Item", on_delete=models.PROTECT, related_name="stock_movements")
    location = models.ForeignKey(StockLocation, on_delete=models.PROTECT, related_name="stock_movements")
    movement_type = models.CharField(max_length=30, choices=MOVEMENT_TYPES)
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    reason = models.CharField(max_length=160, blank=True)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "voorraadmutatie"
        verbose_name_plural = "voorraadmutaties"
        ordering = ["-created_at"]

    @property
    def signed_quantity(self):
        if self.movement_type in ["out", "waste", "sale", "recipe_use"]:
            return self.quantity * Decimal("-1")
        return self.quantity

    def __str__(self):
        return f"{self.item} {self.movement_type} {self.quantity}"


def calculate_stock(item, location=None):
    movements = item.stock_movements.all()

    if location:
        movements = movements.filter(location=location)

    total = Decimal("0")

    for movement in movements:
        total += movement.signed_quantity

    return total

from decimal import Decimal

from django.conf import settings
from django.db import models


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

    base_unit = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="derived_units",
        help_text="Bijvoorbeeld gram als basiseenheid voor kilogram.",
    )
    factor_to_base = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        default=1,
        help_text="Hoeveel basiseenheden zitten er in 1 van deze eenheid. 1 kg is 1000 gram.",
    )

    decimal_places = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "eenheid"
        verbose_name_plural = "eenheden"
        ordering = ["unit_type", "name"]

    def __str__(self):
        return self.symbol

    def get_base_unit(self):
        return self.base_unit or self

    def get_base_unit_id(self):
        if self.base_unit_id:
            return self.base_unit_id

        return self.id

    def to_base_quantity(self, quantity):
        return Decimal(quantity) * self.factor_to_base

    def from_base_quantity(self, quantity):
        if self.factor_to_base == 0:
            return Decimal("0")

        return Decimal(quantity) / self.factor_to_base

    def can_convert_to(self, other_unit):
        if other_unit is None:
            return False

        return self.get_base_unit_id() == other_unit.get_base_unit_id()


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
        ("purchase", "Inkoop"),
        ("sale", "Verkoop"),
        ("recipe_use", "Receptverbruik"),
        ("correction_in", "Correctie erbij"),
        ("correction_out", "Correctie eraf"),
        ("return", "Retour erbij"),
        ("waste", "Derving"),
        ("expired", "Over datum"),
        ("breakage", "Breuk of schade"),
        ("donation", "Donatie"),
        ("internal_use", "Intern gebruik"),
    ]

    REASON_CODES = [
        ("purchase", "Inkoop"),
        ("sale", "Verkoop"),
        ("manual_count_plus", "Telling, erbij"),
        ("manual_count_minus", "Telling, eraf"),
        ("correction_plus", "Correctie erbij"),
        ("correction_minus", "Correctie eraf"),
        ("waste", "Derving"),
        ("expired", "Over datum"),
        ("breakage", "Breuk of schade"),
        ("donation", "Donatie"),
        ("internal_use", "Intern gebruik"),
        ("recipe_use", "Verbruikt in recept"),
        ("return", "Retour"),
        ("other", "Overig"),
    ]

    NEGATIVE_MOVEMENT_TYPES = {
        "out",
        "sale",
        "recipe_use",
        "correction_out",
        "waste",
        "expired",
        "breakage",
        "donation",
        "internal_use",
    }

    POSITIVE_MOVEMENT_TYPES = {
        "in",
        "purchase",
        "correction_in",
        "return",
    }

    item = models.ForeignKey("items.Item", on_delete=models.PROTECT, related_name="stock_movements")
    location = models.ForeignKey(StockLocation, on_delete=models.PROTECT, related_name="stock_movements")
    movement_type = models.CharField(max_length=30, choices=MOVEMENT_TYPES)

    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="stock_movements",
        help_text="Laat leeg om de vaste voorraadeenheid van het item te gebruiken.",
    )

    reason_code = models.CharField(max_length=40, choices=REASON_CODES, default="other")
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
        permissions = [
            ("can_adjust_stock", "Kan voorraad opboeken en afboeken"),
            ("can_view_stock_dashboard", "Kan voorraadbeheer bekijken"),
        ]

    @property
    def effective_unit(self):
        return self.unit or self.item.unit

    @property
    def quantity_in_item_unit(self):
        movement_unit = self.effective_unit
        item_unit = self.item.unit

        if not movement_unit or not item_unit:
            return self.quantity

        if movement_unit == item_unit:
            return self.quantity

        if not movement_unit.can_convert_to(item_unit):
            return self.quantity

        base_quantity = movement_unit.to_base_quantity(self.quantity)
        return item_unit.from_base_quantity(base_quantity)

    @property
    def signed_quantity(self):
        quantity = self.quantity_in_item_unit

        if self.movement_type in self.NEGATIVE_MOVEMENT_TYPES:
            return quantity * Decimal("-1")

        return quantity

    @property
    def direction_label(self):
        if self.movement_type in self.NEGATIVE_MOVEMENT_TYPES:
            return "Eraf"

        return "Erbij"

    def __str__(self):
        unit = self.effective_unit.symbol if self.effective_unit else ""
        return f"{self.item} {self.get_movement_type_display()} {self.quantity} {unit}"


def calculate_stock(item, location=None):
    movements = item.stock_movements.all()

    if location:
        movements = movements.filter(location=location)

    total = Decimal("0")

    for movement in movements:
        total += movement.signed_quantity

    return total


def item_is_available(item):
    if item.status != "active":
        return False

    if item.item_type in ["menu_item", "drink"]:
        try:
            from apps.recipes.models import get_recipe_availability

            availability = get_recipe_availability(item)

            if availability["has_recipe"]:
                return availability["is_available"]
        except Exception:
            pass

    if not item.is_stock_tracked:
        return True

    return calculate_stock(item) > Decimal("0")

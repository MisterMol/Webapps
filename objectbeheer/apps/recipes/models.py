from decimal import Decimal

from django.db import models, transaction

from apps.inventory.services import book_stock


class Recipe(models.Model):
    output_item = models.OneToOneField(
        "items.Item",
        on_delete=models.CASCADE,
        related_name="recipe",
    )
    servings = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    instructions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "recept"
        verbose_name_plural = "recepten"

    def __str__(self):
        return f"Recept voor {self.output_item.name}"


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ingredients")
    ingredient = models.ForeignKey(
        "items.Item",
        on_delete=models.PROTECT,
        related_name="used_in_recipes",
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    waste_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        verbose_name = "receptingrediënt"
        verbose_name_plural = "receptingrediënten"
        unique_together = ("recipe", "ingredient")

    def total_quantity_with_waste(self, multiplier=1):
        base_quantity = self.quantity * Decimal(str(multiplier))
        waste_multiplier = Decimal("1") + (self.waste_percentage / Decimal("100"))
        return base_quantity * waste_multiplier

    def __str__(self):
        unit = self.ingredient.unit.symbol if self.ingredient.unit else ""
        return f"{self.quantity} {unit} {self.ingredient.name}"


@transaction.atomic
def consume_recipe_stock(menu_item, quantity_sold, user=None, location=None):
    recipe = menu_item.recipe

    for recipe_line in recipe.ingredients.select_related("ingredient", "ingredient__unit"):
        total_quantity = recipe_line.total_quantity_with_waste(quantity_sold)

        book_stock(
            item=recipe_line.ingredient,
            movement_type="recipe_use",
            quantity=total_quantity,
            user=user,
            location=location,
            reason="Receptverbruik",
            note=f"Verbruikt voor {quantity_sold} x {menu_item.name}",
        )

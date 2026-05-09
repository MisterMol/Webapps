from decimal import Decimal, ROUND_FLOOR

from django.db import models, transaction

from apps.inventory.models import calculate_stock
from apps.inventory.services import book_stock


class Recipe(models.Model):
    output_item = models.OneToOneField(
        "items.Item",
        on_delete=models.CASCADE,
        related_name="recipe",
    )
    servings = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1,
        help_text="Aantal porties of verkoopitems waarvoor deze receptuur geldt.",
    )
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
    is_optional = models.BooleanField(
        default=False,
        help_text="Optionele ingrediënten blokkeren beschikbaarheid niet als ze op zijn.",
    )
    note = models.CharField(max_length=220, blank=True)

    class Meta:
        verbose_name = "receptingrediënt"
        verbose_name_plural = "receptingrediënten"
        unique_together = ("recipe", "ingredient")

    def quantity_for_one_output(self):
        if not self.recipe.servings:
            return self.quantity

        base_quantity = self.quantity / self.recipe.servings
        waste_multiplier = Decimal("1") + (self.waste_percentage / Decimal("100"))

        return base_quantity * waste_multiplier

    def total_quantity_with_waste(self, multiplier=1):
        return self.quantity_for_one_output() * Decimal(str(multiplier))

    def __str__(self):
        unit = self.ingredient.unit.symbol if self.ingredient.unit else ""
        optional = "optioneel" if self.is_optional else "verplicht"
        return f"{self.quantity} {unit} {self.ingredient.name} ({optional})"


def get_recipe_availability(menu_item):
    try:
        recipe = menu_item.recipe
    except Recipe.DoesNotExist:
        return {
            "has_recipe": False,
            "is_available": True,
            "max_outputs": None,
            "required_lines": [],
            "optional_lines": [],
            "missing_required": [],
            "missing_optional": [],
        }

    if not recipe.is_active:
        return {
            "has_recipe": True,
            "is_available": False,
            "max_outputs": Decimal("0"),
            "required_lines": [],
            "optional_lines": [],
            "missing_required": ["Recept is niet actief."],
            "missing_optional": [],
        }

    required_lines = []
    optional_lines = []
    max_outputs = None
    missing_required = []
    missing_optional = []

    for line in recipe.ingredients.select_related("ingredient", "ingredient__unit"):
        ingredient = line.ingredient
        stock = calculate_stock(ingredient)
        needed_for_one = line.quantity_for_one_output()

        if needed_for_one <= 0:
            possible_outputs = None
        else:
            possible_outputs = (stock / needed_for_one).to_integral_value(rounding=ROUND_FLOOR)

        row = {
            "line": line,
            "ingredient": ingredient,
            "stock": stock,
            "needed_for_one": needed_for_one,
            "possible_outputs": possible_outputs,
            "unit": ingredient.unit,
            "is_missing": stock < needed_for_one,
        }

        if line.is_optional:
            optional_lines.append(row)

            if stock < needed_for_one:
                missing_optional.append(row)
        else:
            required_lines.append(row)

            if stock < needed_for_one:
                missing_required.append(row)

            if possible_outputs is not None:
                if max_outputs is None:
                    max_outputs = possible_outputs
                else:
                    max_outputs = min(max_outputs, possible_outputs)

    if max_outputs is None and required_lines:
        max_outputs = Decimal("0")

    if not required_lines:
        max_outputs = None

    return {
        "has_recipe": True,
        "is_available": len(missing_required) == 0,
        "max_outputs": max_outputs,
        "required_lines": required_lines,
        "optional_lines": optional_lines,
        "missing_required": missing_required,
        "missing_optional": missing_optional,
    }


def build_recipe_consumption_plan(menu_item, quantity_sold, overrides=None, include_optional=True):
    overrides = overrides or {}

    recipe = menu_item.recipe
    lines = []

    for recipe_line in recipe.ingredients.select_related("ingredient", "ingredient__unit"):
        if recipe_line.is_optional and not include_optional:
            continue

        ingredient = recipe_line.ingredient

        if ingredient.id in overrides:
            quantity = Decimal(str(overrides[ingredient.id]))
        else:
            quantity = recipe_line.total_quantity_with_waste(quantity_sold)

        if quantity <= 0:
            continue

        lines.append(
            {
                "ingredient": ingredient,
                "quantity": quantity,
                "unit": ingredient.unit,
                "source": "override" if ingredient.id in overrides else "recipe",
                "is_optional": recipe_line.is_optional,
            }
        )

    return lines


@transaction.atomic
def consume_recipe_stock(menu_item, quantity_sold, user=None, location=None, overrides=None, include_optional=True, note=""):
    consumption_lines = build_recipe_consumption_plan(
        menu_item=menu_item,
        quantity_sold=quantity_sold,
        overrides=overrides,
        include_optional=include_optional,
    )

    movements = []

    for line in consumption_lines:
        movement = book_stock(
            item=line["ingredient"],
            movement_type="recipe_use",
            quantity=line["quantity"],
            unit=line["unit"],
            user=user,
            location=location,
            reason_code="recipe_use",
            reason="Receptverbruik",
            note=note or f"Verbruikt voor {quantity_sold} x {menu_item.name}",
        )
        movements.append(movement)

    return movements

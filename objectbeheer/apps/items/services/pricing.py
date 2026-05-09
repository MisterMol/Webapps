from decimal import Decimal, ROUND_HALF_UP


def money(value):
    if value is None:
        return None

    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_recipe_cost(item):
    recipe = getattr(item, "recipe", None)

    if not recipe:
        return None

    total = Decimal("0.00")
    has_prices = False

    for line in recipe.ingredients.select_related("ingredient"):
        ingredient = line.ingredient

        if ingredient.purchase_price is None:
            continue

        has_prices = True

        quantity = Decimal(line.quantity)
        purchase_price = Decimal(ingredient.purchase_price)
        waste_percentage = Decimal(line.waste_percentage or 0)

        line_cost = quantity * purchase_price

        if waste_percentage > 0:
            line_cost = line_cost * (Decimal("1.00") + waste_percentage / Decimal("100"))

        total += line_cost

    if not has_prices:
        return None

    return money(total)


def calculate_margin(item):
    sale_price = item.sale_price
    cost_price = calculate_recipe_cost(item)

    if sale_price is None or cost_price is None:
        return {
            "cost_price": cost_price,
            "gross_margin": None,
            "gross_margin_percentage": None,
        }

    sale_price = Decimal(sale_price)
    gross_margin = sale_price - cost_price

    if sale_price <= 0:
        gross_margin_percentage = None
    else:
        gross_margin_percentage = (gross_margin / sale_price * Decimal("100")).quantize(
            Decimal("0.1"),
            rounding=ROUND_HALF_UP,
        )

    return {
        "cost_price": money(cost_price),
        "gross_margin": money(gross_margin),
        "gross_margin_percentage": gross_margin_percentage,
    }

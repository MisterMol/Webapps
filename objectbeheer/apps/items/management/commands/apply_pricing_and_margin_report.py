import csv
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.items.models import Item
from apps.recipes.models import Recipe


PRICE_BY_NAME = {
    # Basis lunch
    "Jonge kaas": "0.0080",
    "Broodje": "0.3500",
    "Tomaat": "0.0040",

    # Burger basis
    "Brioche burger bun": "0.5500",
    "Brioche bol zwart sesam": "0.6500",
    "Runderburger 150g": "1.7500",
    "Black Angus burger 180g": "2.8500",
    "Smash burger patty": "0.9500",
    "Kipburger krokant": "1.4500",
    "Vega burger": "1.6500",
    "Cheddar plak": "0.2200",
    "IJsbergsla": "0.0060",
    "Rode ui": "0.0025",
    "Augurk": "0.0060",
    "Jalapeño": "0.0070",

    # Friet en snacks
    "Friet aardappel": "0.0020",
    "Zoete aardappel friet": "0.0035",
    "Loaded fries topping spek": "0.0120",
    "Kroket": "0.5500",
    "Frikandel": "0.4800",
    "Kaassoufflé": "0.5500",
    "Bitterbal": "0.2200",
    "Krokante kipstukjes": "0.0140",
    "Chicken Wings 6 stuks": "2.2500",
    "Onion Rings 8 stuks": "1.3500",

    # Vlees, vis en vega
    "Pulled chicken": "0.0120",
    "Falafel": "0.2200",
    "Halloumi": "0.0180",
    "Bacon": "0.0160",

    # Brood en wraps
    "Wrap tortilla": "0.3000",
    "Pitabrood": "0.3000",

    # Groente en toppings
    "Rucola": "0.0150",
    "Komkommer": "0.0030",
    "Avocado": "0.9500",
    "Champignons": "0.0060",
    "Gebakken ui": "0.0060",
    "Krokante uitjes": "0.0080",
    "Nacho crumble": "0.0060",
    "Kimchi": "0.0120",

    # Sauzen per ml
    "Truffelmayonaise": "0.0140",
    "Knoflooksaus": "0.0060",
    "Sambalsaus": "0.0070",
    "Mayonaise": "0.0050",
    "Ketchup": "0.0040",
    "BBQ saus": "0.0060",
    "Burger relish": "0.0080",
    "Sriracha mayo": "0.0090",
    "Andalouse saus": "0.0070",
    "Samurai saus": "0.0080",
    "Satésaus": "0.0100",
    "Joppiesaus": "0.0080",
    "Cheddarsaus": "0.0100",
    "Aioli": "0.0080",
    "Vegan mayo": "0.0090",

    # Kruiden per gram
    "Zout": "0.0005",
    "Paprikapoeder": "0.0060",
    "Suiker": "0.0010",
    "Knoflook kruidenmix": "0.0070",
    "Cajun kruiden": "0.0080",
    "Ras el hanout": "0.0090",

    # Zuivel en dessert
    "Parmezaan": "0.0180",
    "Mozzarella": "0.0100",
    "Slagroom": "0.0060",
    "Vanille ijs": "0.0060",
    "Chocoladesaus": "0.0070",
    "Karamelsaus": "0.0070",

    # Dranken voorraad per ml
    "Amaretto": "0.0180",
    "Citroensap": "0.0040",
    "Suikersiroop": "0.0030",
    "Cocktailkers": "0.0600",
    "Vodka": "0.0160",
    "Rum": "0.0180",
    "Gin": "0.0220",
    "Limoensap": "0.0040",
    "Cola siroop of fles": "0.0030",
    "Tonic": "0.0040",
    "Munt": "0.0200",
    "Tequila": "0.0240",
    "Triple sec": "0.0190",
    "Cointreau": "0.0280",
    "Campari": "0.0220",
    "Aperol": "0.0180",
    "Prosecco": "0.0110",
    "Bourbon": "0.0240",
    "Whiskey": "0.0240",
    "Rode vermouth": "0.0140",
    "Koffielikeur": "0.0190",
    "Espresso": "0.0050",
    "Cranberrysap": "0.0040",
    "Sinaasappelsap": "0.0040",
    "Ananassap": "0.0040",
    "Kokosroom": "0.0060",
    "Ginger beer": "0.0040",
    "Grapefruit soda": "0.0040",
    "Bruiswater": "0.0015",
    "Passievrucht puree": "0.0120",
    "Vanillesiroop": "0.0080",
    "Grenadine": "0.0070",
    "Eiwit of aquafaba": "0.0040",
    "Limoenpartjes": "0.0800",
    "Sinaasappelschijf": "0.0800",
    "Citroenschijf": "0.0800",

    # Losse verkoopproducten zonder recept
    "Cola 330 ml": "0.7000",
    "Kroket los": "0.5500",
    "Bakje truffelmayonaise": "0.7000",
    "Bakje knoflooksaus": "0.3000",
    "Bakje sriracha mayo": "0.4500",
    "Bakje samurai saus": "0.4000",
    "Bakje satésaus": "0.6000",
    "Bakje joppiesaus": "0.4000",
    "Bakje vegan mayo": "0.4500",
}


VAT_21_ITEMS = {
    "Amaretto Sour",
    "Margarita",
    "Espresso Martini",
    "Pornstar Martini",
    "Aperol Spritz",
    "Negroni",
    "Whiskey Sour",
    "Paloma",
    "Piña Colada",
    "Cuba Libre",
    "Dark and Stormy",
    "Mojito",
    "Gin Tonic",
}


SELLABLE_TYPES = {"product", "menu_item", "drink"}


def decimal(value):
    if value in [None, ""]:
        return None

    return Decimal(str(value))


def money(value):
    if value is None:
        return ""

    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def percentage(value):
    if value is None:
        return ""

    return str(value.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def suggested_price(cost, item):
    if cost is None or cost <= 0:
        return None

    category_name = item.category.name.lower() if item.category else ""

    if item.item_type == "drink" and item.name in VAT_21_ITEMS:
        target_margin = Decimal("0.72")
        minimum_price = Decimal("7.50")
    elif item.item_type == "drink":
        target_margin = Decimal("0.70")
        minimum_price = Decimal("2.50")
    elif "saus" in category_name:
        target_margin = Decimal("0.65")
        minimum_price = Decimal("1.00")
    elif item.item_type == "product":
        target_margin = Decimal("0.60")
        minimum_price = Decimal("2.50")
    else:
        target_margin = Decimal("0.68")
        minimum_price = Decimal("3.50")

    raw_price = cost / (Decimal("1.00") - target_margin)

    if raw_price < minimum_price:
        raw_price = minimum_price

    rounded = raw_price.quantize(Decimal("0.50"), rounding=ROUND_HALF_UP)

    cents = rounded % Decimal("1.00")
    if cents == Decimal("0.00"):
        rounded = rounded - Decimal("0.05")

    return rounded.quantize(Decimal("0.01"))


class Command(BaseCommand):
    help = "Past basisprijzen toe en maakt een margeoverzicht."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Schrijf inkoopprijzen en btw correcties echt naar de database.",
        )
        parser.add_argument(
            "--apply-sale-prices",
            action="store_true",
            help="Vul ontbrekende verkoopprijzen met adviesprijzen.",
        )
        parser.add_argument(
            "--overwrite-sale-prices",
            action="store_true",
            help="Overschrijf bestaande verkoopprijzen met adviesprijzen. Voorzichtig gebruiken.",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        apply_sale_prices = options["apply_sale_prices"]
        overwrite_sale_prices = options["overwrite_sale_prices"]

        output_dir = Path("exports/pricing")
        output_dir.mkdir(parents=True, exist_ok=True)

        items_by_id = {
            item.id: item
            for item in Item.objects.select_related("category", "unit").all()
        }

        proposed_prices = {
            name: Decimal(value)
            for name, value in PRICE_BY_NAME.items()
        }

        updated_purchase_prices = []
        updated_vat = []
        updated_sale_prices = []

        with transaction.atomic():
            for item in items_by_id.values():
                proposed_price = proposed_prices.get(item.name)

                if proposed_price is not None and item.purchase_price != proposed_price:
                    updated_purchase_prices.append((item.name, item.purchase_price, proposed_price))

                    if apply_changes:
                        item.purchase_price = proposed_price
                        item.save(update_fields=["purchase_price", "updated_at"])

                if item.name in VAT_21_ITEMS and item.vat_rate != Decimal("21.00"):
                    updated_vat.append((item.name, item.vat_rate, Decimal("21.00")))

                    if apply_changes:
                        item.vat_rate = Decimal("21.00")
                        item.save(update_fields=["vat_rate", "updated_at"])

            report_rows = []

            for item in Item.objects.filter(status="active", item_type__in=SELLABLE_TYPES).select_related("category", "unit").order_by("category__sort_order", "name"):
                recipe = Recipe.objects.filter(output_item=item, is_active=True).first()

                cost_excl_optional = Decimal("0.00")
                cost_incl_optional = Decimal("0.00")
                missing_prices = []

                if recipe:
                    recipe_lines = recipe.ingredients.select_related("ingredient").all()

                    for line in recipe_lines:
                        ingredient = line.ingredient
                        effective_purchase_price = proposed_prices.get(ingredient.name, ingredient.purchase_price)

                        if effective_purchase_price is None:
                            missing_prices.append(ingredient.name)
                            continue

                        quantity = decimal(line.quantity) or Decimal("0.00")
                        waste = decimal(line.waste_percentage) or Decimal("0.00")
                        waste_multiplier = Decimal("1.00") + (waste / Decimal("100.00"))
                        line_cost = effective_purchase_price * quantity * waste_multiplier

                        cost_incl_optional += line_cost

                        if not line.is_optional:
                            cost_excl_optional += line_cost

                    servings = decimal(recipe.servings) or Decimal("1.00")
                    if servings > 0:
                        cost_excl_optional = cost_excl_optional / servings
                        cost_incl_optional = cost_incl_optional / servings
                else:
                    effective_purchase_price = proposed_prices.get(item.name, item.purchase_price)

                    if effective_purchase_price is None:
                        missing_prices.append(item.name)
                    else:
                        cost_excl_optional = effective_purchase_price
                        cost_incl_optional = effective_purchase_price

                sale_price = item.sale_price
                profit = None
                margin = None

                if sale_price is not None:
                    profit = sale_price - cost_incl_optional

                    if sale_price > 0:
                        margin = (profit / sale_price) * Decimal("100.00")

                advice_price = suggested_price(cost_incl_optional, item)

                status = "Prima"

                if missing_prices:
                    status = "Mist inkoopprijs"
                elif sale_price is None:
                    status = "Mist verkoopprijs"
                elif margin is not None and margin < Decimal("55.00"):
                    status = "Marge te laag"
                elif margin is not None and margin < Decimal("65.00"):
                    status = "Let op marge"
                elif margin is not None and margin > Decimal("82.00"):
                    status = "Ruime marge"

                if advice_price is not None:
                    should_update_sale = (
                        apply_changes
                        and (
                            apply_sale_prices and item.sale_price is None
                            or overwrite_sale_prices
                        )
                    )

                    if should_update_sale:
                        updated_sale_prices.append((item.name, item.sale_price, advice_price))
                        item.sale_price = advice_price
                        item.save(update_fields=["sale_price", "updated_at"])

                report_rows.append({
                    "item": item.name,
                    "type": item.get_item_type_display(),
                    "categorie": item.category.name if item.category else "",
                    "btw": money(item.vat_rate),
                    "verkoopprijs": money(sale_price),
                    "kostprijs_excl_optioneel": money(cost_excl_optional),
                    "kostprijs_incl_optioneel": money(cost_incl_optional),
                    "brutowinst": money(profit),
                    "marge_percentage": percentage(margin),
                    "adviesprijs": money(advice_price),
                    "status": status,
                    "mist_inkoopprijs": ", ".join(missing_prices),
                })

            csv_path = output_dir / "margeoverzicht.csv"

            with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(
                    csv_file,
                    fieldnames=[
                        "item",
                        "type",
                        "categorie",
                        "btw",
                        "verkoopprijs",
                        "kostprijs_excl_optioneel",
                        "kostprijs_incl_optioneel",
                        "brutowinst",
                        "marge_percentage",
                        "adviesprijs",
                        "status",
                        "mist_inkoopprijs",
                    ],
                    delimiter=";",
                )
                writer.writeheader()
                writer.writerows(report_rows)

            summary_path = output_dir / "margeoverzicht-samenvatting.txt"

            with summary_path.open("w", encoding="utf-8") as summary_file:
                summary_file.write("Margeoverzicht\n")
                summary_file.write("================\n\n")
                summary_file.write(f"Database aangepast: {'ja' if apply_changes else 'nee'}\n")
                summary_file.write(f"Inkoopprijzen te wijzigen: {len(updated_purchase_prices)}\n")
                summary_file.write(f"Btw correcties te wijzigen: {len(updated_vat)}\n")
                summary_file.write(f"Verkoopprijzen te wijzigen: {len(updated_sale_prices)}\n")
                summary_file.write(f"Rapportregels: {len(report_rows)}\n\n")

                summary_file.write("Items met aandacht:\n")
                for row in report_rows:
                    if row["status"] != "Prima":
                        summary_file.write(
                            f"{row['item']} | {row['status']} | kostprijs {row['kostprijs_incl_optioneel']} | verkoop {row['verkoopprijs']} | marge {row['marge_percentage']}%\n"
                        )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Prijscontrole klaar."))
        self.stdout.write(f"Database aangepast: {'ja' if apply_changes else 'nee'}")
        self.stdout.write(f"Inkoopprijzen te wijzigen: {len(updated_purchase_prices)}")
        self.stdout.write(f"Btw correcties te wijzigen: {len(updated_vat)}")
        self.stdout.write(f"Verkoopprijzen te wijzigen: {len(updated_sale_prices)}")
        self.stdout.write(f"CSV rapport: {csv_path}")
        self.stdout.write(f"Samenvatting: {summary_path}")

        if not apply_changes:
            self.stdout.write("")
            self.stdout.write("Dit was een droge run. Gebruik --apply als je de prijzen echt wilt opslaan.")

from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.inventory.models import StockLocation, StockMovement, Unit
from apps.items.models import Category, Item, Label
from apps.recipes.models import Recipe, RecipeIngredient


class Command(BaseCommand):
    help = "Vult demo-data voor een luxe snackbar met cocktails, burgers, friet, snacks en ingrediënten."

    def handle(self, *args, **options):
        stuk = Unit.objects.get(symbol="stuk")
        gram = Unit.objects.get(symbol="g")
        ml = Unit.objects.get(symbol="ml")
        liter = Unit.objects.get(symbol="l")

        keuken, _ = StockLocation.objects.get_or_create(name="Keuken", defaults={"is_default": True})
        bar, _ = StockLocation.objects.get_or_create(name="Bar")
        magazijn, _ = StockLocation.objects.get_or_create(name="Magazijn")

        categories = {}

        category_names = [
            ("Burgers", 10),
            ("Friet", 20),
            ("Snacks", 30),
            ("Sauzen", 40),
            ("Cocktails", 50),
            ("Frisdrank", 60),
            ("Warme dranken", 70),
            ("Bier en wijn", 80),
            ("Vlees en vis", 100),
            ("Brood en deeg", 110),
            ("Groente en fruit", 120),
            ("Zuivel", 130),
            ("Sauzen en toppings", 140),
            ("Kruiden en smaakmakers", 150),
            ("Dranken voorraad", 160),
            ("Verpakking", 170),
        ]

        for name, sort_order in category_names:
            categories[name], _ = Category.objects.update_or_create(
                name=name,
                defaults={"sort_order": sort_order, "is_active": True},
            )

        labels = {}
        label_data = [
            ("Populair", "#f59e0b"),
            ("Vegetarisch", "#22c55e"),
            ("Vegan", "#16a34a"),
            ("Pittig", "#ef4444"),
            ("Alcoholisch", "#7c3aed"),
            ("Cocktail", "#ec4899"),
            ("Halal mogelijk", "#06b6d4"),
            ("Glutenvrij mogelijk", "#0ea5e9"),
            ("Snack", "#f97316"),
            ("Hardloper", "#84cc16"),
        ]

        for name, color in label_data:
            labels[name], _ = Label.objects.update_or_create(
                name=name,
                defaults={"color": color},
            )

        def make_item(name, item_type, category, unit, stock_tracked=True, sale_price=None, purchase_price=None, stock=0, location=None, labels_to_add=None, description="", short_description=""):
            item, _ = Item.objects.update_or_create(
                name=name,
                defaults={
                    "item_type": item_type,
                    "category": category,
                    "unit": unit,
                    "is_stock_tracked": stock_tracked,
                    "sale_price": sale_price,
                    "purchase_price": purchase_price,
                    "status": "active",
                    "show_image": item_type != "ingredient",
                    "use_default_image_when_missing": True,
                    "short_description": short_description,
                    "description": description,
                    "is_featured": item_type in ["menu_item", "drink", "product"],
                },
            )

            if labels_to_add:
                item.labels.add(*[labels[label_name] for label_name in labels_to_add])

            if stock_tracked and stock:
                exists = StockMovement.objects.filter(
                    item=item,
                    reason="Startvoorraad luxe snackbar",
                ).exists()

                if not exists:
                    StockMovement.objects.create(
                        item=item,
                        location=location or magazijn,
                        movement_type="purchase",
                        quantity=Decimal(str(stock)),
                        unit=unit,
                        reason_code="purchase",
                        reason="Startvoorraad luxe snackbar",
                        note="Demo voorraad.",
                    )

            return item

        ingredients = {}

        ingredient_data = [
            ("Brioche burger bun", "Brood en deeg", stuk, 80, "Broodje voor burgers."),
            ("Runderburger 150g", "Vlees en vis", stuk, 60, "Burgerpatty van rundvlees."),
            ("Kipburger krokant", "Vlees en vis", stuk, 45, "Krokante kipburger."),
            ("Vega burger", "Vlees en vis", stuk, 35, "Vegetarische burger."),
            ("Cheddar plak", "Zuivel", stuk, 120, "Plak cheddar."),
            ("IJsbergsla", "Groente en fruit", gram, 3000, "Frisse sla."),
            ("Tomaat", "Groente en fruit", gram, 3500, "Verse tomaat."),
            ("Rode ui", "Groente en fruit", gram, 2000, "Rode ui."),
            ("Augurk", "Sauzen en toppings", gram, 1800, "Augurkenschijfjes."),
            ("Jalapeño", "Sauzen en toppings", gram, 900, "Pittige jalapeño."),
            ("Friet aardappel", "Friet", gram, 25000, "Frietvoorraad."),
            ("Zoete aardappel friet", "Friet", gram, 9000, "Zoete aardappel friet."),
            ("Loaded fries topping spek", "Vlees en vis", gram, 2500, "Spek topping."),
            ("Truffelmayonaise", "Sauzen en toppings", ml, 2500, "Truffelmayonaise."),
            ("Knoflooksaus", "Sauzen en toppings", ml, 3000, "Knoflooksaus."),
            ("Sambalsaus", "Sauzen en toppings", ml, 1800, "Pittige sambalsaus."),
            ("Mayonaise", "Sauzen en toppings", ml, 5000, "Mayonaise."),
            ("Ketchup", "Sauzen en toppings", ml, 4500, "Ketchup."),
            ("Zout", "Kruiden en smaakmakers", gram, 2000, "Zout."),
            ("Paprikapoeder", "Kruiden en smaakmakers", gram, 800, "Paprikapoeder."),
            ("Suiker", "Kruiden en smaakmakers", gram, 3000, "Suiker."),
            ("Kroket", "Snacks", stuk, 96, "Kroketten."),
            ("Frikandel", "Snacks", stuk, 120, "Frikandellen."),
            ("Kaassoufflé", "Snacks", stuk, 80, "Kaassoufflés."),
            ("Bitterbal", "Snacks", stuk, 240, "Bitterballen."),
            ("Amaretto", "Dranken voorraad", ml, 1200, "Amaretto likeur."),
            ("Vodka", "Dranken voorraad", ml, 1400, "Vodka."),
            ("Rum", "Dranken voorraad", ml, 1000, "Rum."),
            ("Gin", "Dranken voorraad", ml, 1000, "Gin."),
            ("Citroensap", "Dranken voorraad", ml, 2500, "Citroensap."),
            ("Limoensap", "Dranken voorraad", ml, 2000, "Limoensap."),
            ("Suikersiroop", "Dranken voorraad", ml, 2500, "Suikersiroop."),
            ("Cola siroop of fles", "Dranken voorraad", ml, 8000, "Cola voorraad."),
            ("Tonic", "Dranken voorraad", ml, 6000, "Tonic."),
            ("Munt", "Groente en fruit", gram, 300, "Munt."),
            ("Cocktailkers", "Sauzen en toppings", stuk, 0, "Optionele garnering."),
        ]

        for name, category_name, unit, stock, description in ingredient_data:
            ingredients[name] = make_item(
                name=name,
                item_type="ingredient",
                category=categories[category_name],
                unit=unit,
                stock_tracked=True,
                purchase_price=Decimal("0.01"),
                stock=stock,
                location=bar if category_name == "Dranken voorraad" else keuken,
                description=description,
                short_description=description,
            )

        sale_items = {}

        sale_item_data = [
            ("Classic Burger", "menu_item", "Burgers", Decimal("9.50"), ["Populair"], "Brioche bun, runderburger, sla, tomaat, ui en burgersaus."),
            ("Cheese Burger", "menu_item", "Burgers", Decimal("10.50"), ["Populair"], "Classic burger met cheddar."),
            ("Spicy Jalapeño Burger", "menu_item", "Burgers", Decimal("11.50"), ["Pittig"], "Burger met jalapeño en sambalsaus."),
            ("Vega Truffel Burger", "menu_item", "Burgers", Decimal("11.00"), ["Vegetarisch"], "Vega burger met truffelmayonaise."),
            ("Friet normaal", "menu_item", "Friet", Decimal("3.50"), ["Hardloper"], "Krokante friet met zout."),
            ("Friet truffel", "menu_item", "Friet", Decimal("5.50"), ["Vegetarisch"], "Friet met truffelmayonaise en kruiden."),
            ("Loaded fries bacon", "menu_item", "Friet", Decimal("7.50"), ["Populair"], "Friet met cheddar en spek topping."),
            ("Kroket los", "product", "Snacks", Decimal("2.75"), ["Snack"], "Losse kroket."),
            ("Frikandel speciaal", "menu_item", "Snacks", Decimal("3.75"), ["Snack"], "Frikandel met saus en ui."),
            ("Bitterballen 8 stuks", "menu_item", "Snacks", Decimal("7.95"), ["Snack", "Populair"], "Portie bitterballen."),
            ("Bakje truffelmayonaise", "product", "Sauzen", Decimal("1.25"), ["Vegetarisch"], "Los bakje truffelmayonaise."),
            ("Bakje knoflooksaus", "product", "Sauzen", Decimal("1.00"), ["Vegetarisch"], "Los bakje knoflooksaus."),
            ("Amaretto Sour", "drink", "Cocktails", Decimal("8.50"), ["Cocktail", "Alcoholisch", "Populair"], "Amaretto, citroen en suikersiroop. Cocktailkers optioneel."),
            ("Mojito", "drink", "Cocktails", Decimal("9.00"), ["Cocktail", "Alcoholisch"], "Rum, limoen, munt en suiker."),
            ("Gin Tonic", "drink", "Cocktails", Decimal("8.75"), ["Cocktail", "Alcoholisch"], "Gin met tonic."),
            ("Cola", "drink", "Frisdrank", Decimal("2.75"), [], "Cola met ijs."),
            ("Tonic", "drink", "Frisdrank", Decimal("2.75"), [], "Tonic."),
            ("Koffie", "drink", "Warme dranken", Decimal("2.50"), [], "Verse koffie."),
        ]

        for name, item_type, category_name, price, label_names, description in sale_item_data:
            sale_items[name] = make_item(
                name=name,
                item_type=item_type,
                category=categories[category_name],
                unit=stuk,
                stock_tracked=False,
                sale_price=price,
                purchase_price=None,
                labels_to_add=label_names,
                description=description,
                short_description=description,
            )

        def recipe(output_name, lines):
            output_item = sale_items[output_name]
            recipe_obj, _ = Recipe.objects.get_or_create(output_item=output_item, defaults={"servings": 1})

            for ingredient_name, quantity, optional in lines:
                RecipeIngredient.objects.update_or_create(
                    recipe=recipe_obj,
                    ingredient=ingredients[ingredient_name],
                    defaults={
                        "quantity": Decimal(str(quantity)),
                        "waste_percentage": Decimal("0"),
                        "is_optional": optional,
                        "note": "Optioneel" if optional else "",
                    },
                )

        recipe("Classic Burger", [
            ("Brioche burger bun", 1, False),
            ("Runderburger 150g", 1, False),
            ("IJsbergsla", 20, False),
            ("Tomaat", 30, False),
            ("Rode ui", 10, True),
            ("Mayonaise", 20, False),
            ("Augurk", 15, True),
        ])

        recipe("Cheese Burger", [
            ("Brioche burger bun", 1, False),
            ("Runderburger 150g", 1, False),
            ("Cheddar plak", 1, False),
            ("IJsbergsla", 20, False),
            ("Tomaat", 30, False),
            ("Rode ui", 10, True),
            ("Mayonaise", 20, False),
        ])

        recipe("Spicy Jalapeño Burger", [
            ("Brioche burger bun", 1, False),
            ("Runderburger 150g", 1, False),
            ("Cheddar plak", 1, True),
            ("Jalapeño", 20, False),
            ("Sambalsaus", 25, False),
            ("IJsbergsla", 20, False),
        ])

        recipe("Vega Truffel Burger", [
            ("Brioche burger bun", 1, False),
            ("Vega burger", 1, False),
            ("Truffelmayonaise", 25, False),
            ("IJsbergsla", 20, False),
            ("Tomaat", 30, False),
        ])

        recipe("Friet normaal", [
            ("Friet aardappel", 250, False),
            ("Zout", 2, True),
        ])

        recipe("Friet truffel", [
            ("Friet aardappel", 250, False),
            ("Truffelmayonaise", 30, False),
            ("Paprikapoeder", 1, True),
        ])

        recipe("Loaded fries bacon", [
            ("Friet aardappel", 300, False),
            ("Cheddar plak", 1, False),
            ("Loaded fries topping spek", 50, False),
            ("Sambalsaus", 15, True),
        ])

        recipe("Frikandel speciaal", [
            ("Frikandel", 1, False),
            ("Mayonaise", 25, False),
            ("Ketchup", 20, False),
            ("Rode ui", 20, True),
        ])

        recipe("Bitterballen 8 stuks", [
            ("Bitterbal", 8, False),
            ("Mosterd", 15, True),
        ]) if "Mosterd" in ingredients else None

        recipe("Bakje truffelmayonaise", [
            ("Truffelmayonaise", 50, False),
        ])

        recipe("Bakje knoflooksaus", [
            ("Knoflooksaus", 50, False),
        ])

        recipe("Amaretto Sour", [
            ("Amaretto", 50, False),
            ("Citroensap", 25, False),
            ("Suikersiroop", 15, False),
            ("Cocktailkers", 1, True),
        ])

        recipe("Mojito", [
            ("Rum", 50, False),
            ("Limoensap", 25, False),
            ("Munt", 5, False),
            ("Suiker", 10, False),
        ])

        recipe("Gin Tonic", [
            ("Gin", 50, False),
            ("Tonic", 150, False),
        ])

        recipe("Cola", [
            ("Cola siroop of fles", 250, False),
        ])

        recipe("Tonic", [
            ("Tonic", 250, False),
        ])

        self.stdout.write(self.style.SUCCESS("Luxe snackbar demo-data is aangemaakt."))

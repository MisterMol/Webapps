from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.inventory.models import StockLocation, StockMovement, Unit
from apps.items.models import Category, Item, Label
from apps.recipes.models import Recipe, RecipeIngredient, get_recipe_availability


class Command(BaseCommand):
    help = "Voegt extra cocktails, dranken, sauzen, gerechten en recepten toe voor luxe snackbar demo."

    def handle(self, *args, **options):
        stuk = Unit.objects.get(symbol="stuk")
        gram = Unit.objects.get(symbol="g")
        ml = Unit.objects.get(symbol="ml")

        keuken, _ = StockLocation.objects.get_or_create(
            name="Keuken",
            defaults={"is_default": True, "is_active": True},
        )
        bar, _ = StockLocation.objects.get_or_create(
            name="Bar",
            defaults={"is_active": True},
        )
        magazijn, _ = StockLocation.objects.get_or_create(
            name="Magazijn",
            defaults={"is_active": True},
        )

        categories = {}

        category_data = [
            ("Burgers", 10),
            ("Friet", 20),
            ("Snacks", 30),
            ("Sauzen", 40),
            ("Loaded Fries", 45),
            ("Broodjes", 48),
            ("Cocktails", 50),
            ("Mocktails", 55),
            ("Frisdrank", 60),
            ("Warme dranken", 70),
            ("Bier en wijn", 80),
            ("Milkshakes", 90),
            ("Desserts", 95),
            ("Vlees en vis", 100),
            ("Brood en deeg", 110),
            ("Groente en fruit", 120),
            ("Zuivel", 130),
            ("Sauzen en toppings", 140),
            ("Kruiden en smaakmakers", 150),
            ("Dranken voorraad", 160),
            ("Verpakking", 170),
        ]

        for name, sort_order in category_data:
            categories[name], _ = Category.objects.update_or_create(
                name=name,
                defaults={
                    "sort_order": sort_order,
                    "is_active": True,
                },
            )

        labels = {}

        label_data = [
            ("Populair", "#f59e0b"),
            ("Vegetarisch", "#22c55e"),
            ("Vegan", "#16a34a"),
            ("Pittig", "#ef4444"),
            ("Alcoholisch", "#7c3aed"),
            ("Cocktail", "#ec4899"),
            ("Mocktail", "#06b6d4"),
            ("Halal mogelijk", "#0ea5e9"),
            ("Glutenvrij mogelijk", "#38bdf8"),
            ("Snack", "#f97316"),
            ("Hardloper", "#84cc16"),
            ("Nieuw", "#6366f1"),
            ("Zoet", "#f472b6"),
            ("Fris", "#14b8a6"),
            ("Premium", "#111827"),
        ]

        for name, color in label_data:
            labels[name], _ = Label.objects.update_or_create(
                name=name,
                defaults={"color": color},
            )

        def make_item(
            name,
            item_type,
            category_name,
            unit,
            stock_tracked=True,
            sale_price=None,
            purchase_price=None,
            stock=None,
            location=None,
            label_names=None,
            description="",
            short_description="",
            vat_rate=9,
            show_image=None,
            featured=False,
        ):
            category = categories[category_name]

            if show_image is None:
                show_image = item_type != "ingredient"

            item, _ = Item.objects.update_or_create(
                name=name,
                defaults={
                    "item_type": item_type,
                    "category": category,
                    "unit": unit,
                    "is_stock_tracked": stock_tracked,
                    "sale_price": sale_price,
                    "purchase_price": purchase_price,
                    "vat_rate": Decimal(str(vat_rate)),
                    "status": "active",
                    "show_image": show_image,
                    "use_default_image_when_missing": True,
                    "short_description": short_description or description,
                    "description": description or short_description,
                    "is_featured": featured,
                },
            )

            if label_names:
                item.labels.add(*[labels[label_name] for label_name in label_names if label_name in labels])

            if stock_tracked and stock is not None:
                reason = "Startvoorraad extra horeca demo"

                exists = StockMovement.objects.filter(
                    item=item,
                    reason=reason,
                ).exists()

                if not exists and Decimal(str(stock)) > 0:
                    StockMovement.objects.create(
                        item=item,
                        location=location or magazijn,
                        movement_type="purchase",
                        quantity=Decimal(str(stock)),
                        unit=unit,
                        reason_code="purchase",
                        reason=reason,
                        note="Aangemaakt via extra horeca seed.",
                    )

            return item

        ingredients = {}

        ingredient_data = [
            ("Black Angus burger 180g", "Vlees en vis", stuk, 48, "Premium runderburger."),
            ("Smash burger patty", "Vlees en vis", stuk, 90, "Dunne burgerpatty voor smash burgers."),
            ("Pulled chicken", "Vlees en vis", gram, 4000, "Gegaarde pulled chicken."),
            ("Krokante kipstukjes", "Vlees en vis", gram, 5000, "Kipstukjes voor loaded fries en wraps."),
            ("Falafel", "Vlees en vis", stuk, 80, "Vegetarische falafel."),
            ("Halloumi", "Zuivel", gram, 2500, "Halloumi voor burgers en bowls."),
            ("Bacon", "Vlees en vis", gram, 3500, "Bacon topping."),
            ("Brioche bol zwart sesam", "Brood en deeg", stuk, 60, "Premium brioche bol."),
            ("Wrap tortilla", "Brood en deeg", stuk, 80, "Tortilla wraps."),
            ("Pitabrood", "Brood en deeg", stuk, 70, "Pitabroodjes."),
            ("Rucola", "Groente en fruit", gram, 1200, "Rucola."),
            ("Komkommer", "Groente en fruit", gram, 2500, "Komkommer."),
            ("Avocado", "Groente en fruit", stuk, 30, "Avocado."),
            ("Champignons", "Groente en fruit", gram, 2200, "Champignons."),
            ("Gebakken ui", "Sauzen en toppings", gram, 1800, "Gebakken ui topping."),
            ("Krokante uitjes", "Sauzen en toppings", gram, 1500, "Krokante uitjes."),
            ("Nacho crumble", "Sauzen en toppings", gram, 1200, "Crunch topping."),
            ("Kimchi", "Sauzen en toppings", gram, 1500, "Kimchi topping."),
            ("BBQ saus", "Sauzen en toppings", ml, 3500, "BBQ saus."),
            ("Burger relish", "Sauzen en toppings", ml, 2500, "Relish voor burgers."),
            ("Sriracha mayo", "Sauzen en toppings", ml, 2200, "Pittige mayonaise."),
            ("Andalouse saus", "Sauzen en toppings", ml, 3000, "Andalouse saus."),
            ("Samurai saus", "Sauzen en toppings", ml, 2800, "Pittige samurai saus."),
            ("Satésaus", "Sauzen en toppings", ml, 3500, "Satésaus."),
            ("Joppiesaus", "Sauzen en toppings", ml, 3000, "Joppiesaus."),
            ("Cheddarsaus", "Sauzen en toppings", ml, 2500, "Cheddarsaus."),
            ("Aioli", "Sauzen en toppings", ml, 2200, "Aioli."),
            ("Vegan mayo", "Sauzen en toppings", ml, 2200, "Vegan mayonaise."),
            ("Knoflook kruidenmix", "Kruiden en smaakmakers", gram, 800, "Knoflook kruidenmix."),
            ("Cajun kruiden", "Kruiden en smaakmakers", gram, 900, "Cajun kruiden."),
            ("Ras el hanout", "Kruiden en smaakmakers", gram, 700, "Ras el hanout."),
            ("Parmezaan", "Zuivel", gram, 1800, "Geraspte parmezaan."),
            ("Mozzarella", "Zuivel", gram, 2500, "Mozzarella."),
            ("Slagroom", "Zuivel", ml, 2500, "Slagroom."),
            ("Vanille ijs", "Zuivel", gram, 4000, "Vanille ijs."),
            ("Chocoladesaus", "Sauzen en toppings", ml, 2000, "Chocoladesaus."),
            ("Karamelsaus", "Sauzen en toppings", ml, 2000, "Karamelsaus."),
            ("Tequila", "Dranken voorraad", ml, 1400, "Tequila."),
            ("Triple sec", "Dranken voorraad", ml, 1200, "Sinaasappellikeur."),
            ("Cointreau", "Dranken voorraad", ml, 1000, "Premium sinaasappellikeur."),
            ("Campari", "Dranken voorraad", ml, 1000, "Campari."),
            ("Aperol", "Dranken voorraad", ml, 1600, "Aperol."),
            ("Prosecco", "Dranken voorraad", ml, 4500, "Prosecco."),
            ("Bourbon", "Dranken voorraad", ml, 1200, "Bourbon whiskey."),
            ("Whiskey", "Dranken voorraad", ml, 1200, "Whiskey."),
            ("Rode vermouth", "Dranken voorraad", ml, 1000, "Rode vermouth."),
            ("Koffielikeur", "Dranken voorraad", ml, 1200, "Koffielikeur."),
            ("Espresso", "Dranken voorraad", ml, 2500, "Espresso voorraad."),
            ("Cranberrysap", "Dranken voorraad", ml, 4000, "Cranberrysap."),
            ("Sinaasappelsap", "Dranken voorraad", ml, 5000, "Sinaasappelsap."),
            ("Ananassap", "Dranken voorraad", ml, 5000, "Ananassap."),
            ("Kokosroom", "Dranken voorraad", ml, 2500, "Kokosroom."),
            ("Ginger beer", "Dranken voorraad", ml, 5000, "Ginger beer."),
            ("Grapefruit soda", "Dranken voorraad", ml, 4000, "Grapefruit soda."),
            ("Bruiswater", "Dranken voorraad", ml, 8000, "Bruiswater."),
            ("Passievrucht puree", "Dranken voorraad", ml, 2500, "Passievrucht puree."),
            ("Vanillesiroop", "Dranken voorraad", ml, 1800, "Vanillesiroop."),
            ("Grenadine", "Dranken voorraad", ml, 1600, "Grenadine."),
            ("Eiwit of aquafaba", "Dranken voorraad", ml, 1000, "Schuimlaag voor sours."),
            ("Limoenpartjes", "Groente en fruit", stuk, 80, "Garnering."),
            ("Sinaasappelschijf", "Groente en fruit", stuk, 80, "Garnering."),
            ("Citroenschijf", "Groente en fruit", stuk, 80, "Garnering."),
        ]

        for name, category_name, unit, stock, description in ingredient_data:
            ingredients[name] = make_item(
                name=name,
                item_type="ingredient",
                category_name=category_name,
                unit=unit,
                stock_tracked=True,
                purchase_price=Decimal("0.01"),
                stock=stock,
                location=bar if category_name == "Dranken voorraad" else keuken,
                description=description,
                short_description=description,
                vat_rate=9,
                show_image=False,
            )

        existing_ingredients = Item.objects.filter(item_type="ingredient")
        for ingredient in existing_ingredients:
            ingredients.setdefault(ingredient.name, ingredient)

        sale_items = {}

        def make_sale(name, item_type, category_name, price, labels_for_item, description, vat_rate=9, featured=True):
            sale_items[name] = make_item(
                name=name,
                item_type=item_type,
                category_name=category_name,
                unit=stuk,
                stock_tracked=False,
                sale_price=Decimal(str(price)),
                purchase_price=None,
                label_names=labels_for_item,
                description=description,
                short_description=description,
                vat_rate=vat_rate,
                featured=featured,
            )
            return sale_items[name]

        sale_data = [
            ("Black Angus Deluxe", "menu_item", "Burgers", "13.50", ["Premium", "Populair"], "Premium burger met Black Angus, cheddar, bacon, relish en brioche."),
            ("Double Smash Burger", "menu_item", "Burgers", "12.95", ["Populair"], "Dubbele smash burger met cheddar, augurk en burgersaus."),
            ("Korean Chicken Burger", "menu_item", "Burgers", "12.50", ["Pittig", "Nieuw"], "Krokante kipburger met kimchi en sriracha mayo."),
            ("Halloumi Burger", "menu_item", "Burgers", "11.95", ["Vegetarisch"], "Halloumi burger met rucola, tomaat en aioli."),
            ("Falafel Wrap", "menu_item", "Broodjes", "8.95", ["Vegetarisch", "Vegan"], "Wrap met falafel, komkommer, sla en vegan mayo."),
            ("Pulled Chicken Wrap", "menu_item", "Broodjes", "9.95", ["Populair"], "Wrap met pulled chicken, BBQ saus en rucola."),
            ("Loaded Fries Korean Chicken", "menu_item", "Loaded Fries", "8.95", ["Pittig", "Nieuw"], "Friet met krokante kip, kimchi, sriracha mayo en krokante uitjes."),
            ("Loaded Fries Truffle Parmesan", "menu_item", "Loaded Fries", "8.50", ["Vegetarisch", "Premium"], "Friet met truffelmayonaise, parmezaan en rucola."),
            ("Loaded Fries Saté", "menu_item", "Loaded Fries", "7.95", ["Populair"], "Friet met satésaus, krokante uitjes en kruiden."),
            ("Sweet Potato Fries", "menu_item", "Friet", "5.25", ["Vegetarisch"], "Zoete aardappel friet met aioli."),
            ("Chicken Wings 6 stuks", "menu_item", "Snacks", "7.50", ["Snack", "Pittig"], "Krokante chicken wings met BBQ saus."),
            ("Onion Rings 8 stuks", "menu_item", "Snacks", "5.95", ["Vegetarisch", "Snack"], "Krokante onion rings met aioli."),
            ("Snackmix Deluxe", "menu_item", "Snacks", "13.95", ["Snack", "Populair"], "Mix van bitterballen, kaassoufflé, onion rings en kroketstukjes."),
            ("Bakje sriracha mayo", "product", "Sauzen", "1.25", ["Pittig"], "Los bakje sriracha mayo."),
            ("Bakje samurai saus", "product", "Sauzen", "1.25", ["Pittig"], "Los bakje samurai saus."),
            ("Bakje satésaus", "product", "Sauzen", "1.50", ["Vegetarisch"], "Los bakje satésaus."),
            ("Bakje joppiesaus", "product", "Sauzen", "1.25", ["Vegetarisch"], "Los bakje joppiesaus."),
            ("Bakje vegan mayo", "product", "Sauzen", "1.25", ["Vegan"], "Los bakje vegan mayo."),
            ("Margarita", "drink", "Cocktails", "9.50", ["Cocktail", "Alcoholisch", "Fris"], "Tequila, triple sec en limoensap.", 21),
            ("Espresso Martini", "drink", "Cocktails", "9.75", ["Cocktail", "Alcoholisch", "Populair"], "Vodka, espresso en koffielikeur.", 21),
            ("Pornstar Martini", "drink", "Cocktails", "10.50", ["Cocktail", "Alcoholisch", "Premium"], "Vanille, passievrucht en vodka.", 21),
            ("Aperol Spritz", "drink", "Cocktails", "8.75", ["Cocktail", "Alcoholisch", "Fris"], "Aperol, prosecco en bruiswater.", 21),
            ("Negroni", "drink", "Cocktails", "9.95", ["Cocktail", "Alcoholisch", "Premium"], "Gin, Campari en rode vermouth.", 21),
            ("Whiskey Sour", "drink", "Cocktails", "9.50", ["Cocktail", "Alcoholisch"], "Whiskey, citroen, suikersiroop en schuim.", 21),
            ("Paloma", "drink", "Cocktails", "8.95", ["Cocktail", "Alcoholisch", "Fris"], "Tequila, limoen en grapefruit soda.", 21),
            ("Piña Colada", "drink", "Cocktails", "9.50", ["Cocktail", "Alcoholisch", "Zoet"], "Rum, kokosroom en ananassap.", 21),
            ("Cuba Libre", "drink", "Cocktails", "8.50", ["Cocktail", "Alcoholisch"], "Rum, cola en limoen.", 21),
            ("Dark and Stormy", "drink", "Cocktails", "8.95", ["Cocktail", "Alcoholisch"], "Rum, ginger beer en limoen.", 21),
            ("Virgin Mojito", "drink", "Mocktails", "6.50", ["Mocktail", "Fris"], "Munt, limoen, suiker en bruiswater zonder alcohol."),
            ("Passion Fruit Cooler", "drink", "Mocktails", "6.75", ["Mocktail", "Fris"], "Passievrucht, limoen en bruiswater."),
            ("Strawberry Milkshake", "drink", "Milkshakes", "5.50", ["Zoet"], "Milkshake met aardbeiensiroop en vanille ijs."),
            ("Chocolate Milkshake", "drink", "Milkshakes", "5.50", ["Zoet"], "Milkshake met chocoladesaus en vanille ijs."),
            ("Vanilla Milkshake", "drink", "Milkshakes", "5.25", ["Zoet"], "Klassieke vanille milkshake."),
        ]

        for item in sale_data:
            if len(item) == 6:
                name, item_type, category_name, price, label_names, description = item
                make_sale(name, item_type, category_name, price, label_names, description)
            else:
                name, item_type, category_name, price, label_names, description, vat_rate = item
                make_sale(name, item_type, category_name, price, label_names, description, vat_rate=vat_rate)

        def add_recipe(output_name, lines):
            output_item = sale_items.get(output_name) or Item.objects.get(name=output_name)
            recipe, _ = Recipe.objects.get_or_create(output_item=output_item, defaults={"servings": 1})

            for ingredient_name, quantity, optional in lines:
                ingredient = ingredients.get(ingredient_name)

                if ingredient is None:
                    self.stdout.write(self.style.WARNING(f"Ingrediënt ontbreekt en is overgeslagen: {ingredient_name}"))
                    continue

                RecipeIngredient.objects.update_or_create(
                    recipe=recipe,
                    ingredient=ingredient,
                    defaults={
                        "quantity": Decimal(str(quantity)),
                        "waste_percentage": Decimal("0"),
                        "is_optional": optional,
                        "note": "Optioneel" if optional else "",
                    },
                )

        recipes = {
            "Black Angus Deluxe": [
                ("Brioche bol zwart sesam", 1, False),
                ("Black Angus burger 180g", 1, False),
                ("Cheddar plak", 1, False),
                ("Bacon", 30, True),
                ("Burger relish", 25, False),
                ("IJsbergsla", 20, False),
                ("Tomaat", 30, False),
                ("Augurk", 15, True),
            ],
            "Double Smash Burger": [
                ("Brioche burger bun", 1, False),
                ("Smash burger patty", 2, False),
                ("Cheddar plak", 2, False),
                ("Augurk", 20, True),
                ("Mayonaise", 20, False),
                ("Ketchup", 15, False),
            ],
            "Korean Chicken Burger": [
                ("Brioche burger bun", 1, False),
                ("Krokante kipstukjes", 160, False),
                ("Kimchi", 30, True),
                ("Sriracha mayo", 25, False),
                ("IJsbergsla", 20, False),
                ("Krokante uitjes", 10, True),
            ],
            "Halloumi Burger": [
                ("Brioche burger bun", 1, False),
                ("Halloumi", 120, False),
                ("Rucola", 15, False),
                ("Tomaat", 30, False),
                ("Aioli", 25, False),
            ],
            "Falafel Wrap": [
                ("Wrap tortilla", 1, False),
                ("Falafel", 4, False),
                ("Komkommer", 40, False),
                ("IJsbergsla", 25, False),
                ("Vegan mayo", 25, False),
            ],
            "Pulled Chicken Wrap": [
                ("Wrap tortilla", 1, False),
                ("Pulled chicken", 130, False),
                ("BBQ saus", 30, False),
                ("Rucola", 15, True),
                ("Rode ui", 15, True),
            ],
            "Loaded Fries Korean Chicken": [
                ("Friet aardappel", 300, False),
                ("Krokante kipstukjes", 120, False),
                ("Kimchi", 40, True),
                ("Sriracha mayo", 35, False),
                ("Krokante uitjes", 15, True),
            ],
            "Loaded Fries Truffle Parmesan": [
                ("Friet aardappel", 300, False),
                ("Truffelmayonaise", 35, False),
                ("Parmezaan", 20, False),
                ("Rucola", 10, True),
            ],
            "Loaded Fries Saté": [
                ("Friet aardappel", 300, False),
                ("Satésaus", 60, False),
                ("Krokante uitjes", 15, True),
                ("Cajun kruiden", 2, True),
            ],
            "Sweet Potato Fries": [
                ("Zoete aardappel friet", 250, False),
                ("Aioli", 35, False),
                ("Zout", 2, True),
            ],
            "Chicken Wings 6 stuks": [
                ("Krokante kipstukjes", 300, False),
                ("BBQ saus", 40, True),
                ("Cajun kruiden", 3, True),
            ],
            "Onion Rings 8 stuks": [
                ("Rode ui", 160, False),
                ("Aioli", 35, True),
            ],
            "Snackmix Deluxe": [
                ("Bitterbal", 6, False),
                ("Kaassoufflé", 2, False),
                ("Kroket", 2, False),
                ("Aioli", 25, True),
                ("BBQ saus", 25, True),
            ],
            "Bakje sriracha mayo": [
                ("Sriracha mayo", 50, False),
            ],
            "Bakje samurai saus": [
                ("Samurai saus", 50, False),
            ],
            "Bakje satésaus": [
                ("Satésaus", 60, False),
            ],
            "Bakje joppiesaus": [
                ("Joppiesaus", 50, False),
            ],
            "Bakje vegan mayo": [
                ("Vegan mayo", 50, False),
            ],
            "Margarita": [
                ("Tequila", 50, False),
                ("Triple sec", 25, False),
                ("Limoensap", 25, False),
                ("Limoenpartjes", 1, True),
            ],
            "Espresso Martini": [
                ("Vodka", 50, False),
                ("Espresso", 30, False),
                ("Koffielikeur", 25, False),
                ("Suikersiroop", 10, True),
            ],
            "Pornstar Martini": [
                ("Vodka", 40, False),
                ("Passievrucht puree", 40, False),
                ("Vanillesiroop", 15, False),
                ("Limoensap", 15, False),
                ("Prosecco", 60, True),
            ],
            "Aperol Spritz": [
                ("Aperol", 60, False),
                ("Prosecco", 90, False),
                ("Bruiswater", 30, False),
                ("Sinaasappelschijf", 1, True),
            ],
            "Negroni": [
                ("Gin", 30, False),
                ("Campari", 30, False),
                ("Rode vermouth", 30, False),
                ("Sinaasappelschijf", 1, True),
            ],
            "Whiskey Sour": [
                ("Whiskey", 50, False),
                ("Citroensap", 25, False),
                ("Suikersiroop", 15, False),
                ("Eiwit of aquafaba", 20, True),
            ],
            "Paloma": [
                ("Tequila", 50, False),
                ("Limoensap", 15, False),
                ("Grapefruit soda", 120, False),
                ("Limoenpartjes", 1, True),
            ],
            "Piña Colada": [
                ("Rum", 50, False),
                ("Kokosroom", 40, False),
                ("Ananassap", 100, False),
            ],
            "Cuba Libre": [
                ("Rum", 50, False),
                ("Cola siroop of fles", 180, False),
                ("Limoenpartjes", 1, True),
            ],
            "Dark and Stormy": [
                ("Rum", 50, False),
                ("Ginger beer", 150, False),
                ("Limoenpartjes", 1, True),
            ],
            "Virgin Mojito": [
                ("Munt", 5, False),
                ("Limoensap", 25, False),
                ("Suiker", 10, False),
                ("Bruiswater", 150, False),
                ("Limoenpartjes", 1, True),
            ],
            "Passion Fruit Cooler": [
                ("Passievrucht puree", 50, False),
                ("Limoensap", 20, False),
                ("Bruiswater", 150, False),
            ],
            "Strawberry Milkshake": [
                ("Vanille ijs", 180, False),
                ("Slagroom", 80, False),
                ("Grenadine", 20, False),
            ],
            "Chocolate Milkshake": [
                ("Vanille ijs", 180, False),
                ("Slagroom", 80, False),
                ("Chocoladesaus", 30, False),
            ],
            "Vanilla Milkshake": [
                ("Vanille ijs", 200, False),
                ("Slagroom", 80, False),
                ("Vanillesiroop", 20, False),
            ],
        }

        for output_name, lines in recipes.items():
            add_recipe(output_name, lines)

        checked = 0
        unavailable = 0

        for item in Item.objects.filter(status="active", item_type__in=["menu_item", "drink"]):
            availability = get_recipe_availability(item)
            checked += 1

            if availability["has_recipe"] and not availability["is_available"]:
                unavailable += 1
                self.stdout.write(
                    self.style.WARNING(f"Niet beschikbaar door ontbrekende verplichte voorraad: {item.name}")
                )

        self.stdout.write(self.style.SUCCESS(f"Extra horeca demo-data is toegevoegd. Gecontroleerd: {checked}. Niet beschikbaar: {unavailable}."))

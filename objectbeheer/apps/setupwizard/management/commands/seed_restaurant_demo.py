from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.branding.models import BrandingSettings
from apps.company.models import CompanyProfile, CompanySettings
from apps.inventory.models import StockLocation, StockMovement, Unit
from apps.items.models import Category, Item, Label
from apps.recipes.models import Recipe, RecipeIngredient
from apps.setupwizard.models import SetupState


class Command(BaseCommand):
    help = "Maakt demo-inrichting voor Restaurant De Molen."

    def handle(self, *args, **options):
        company, _ = CompanyProfile.objects.get_or_create(
            name="Restaurant De Molen",
            defaults={
                "public_name": "Restaurant De Molen",
                "company_type": "restaurant",
                "email": "info@restaurantdemolen.test",
                "phone": "0123 456 789",
                "address": "Molenstraat 1, 1234 AB Voorbeeldstad",
            },
        )

        CompanySettings.objects.get_or_create(
            company=company,
            defaults={
                "enable_inventory": True,
                "enable_recipes": True,
                "enable_orders": False,
                "enable_public_catalog": True,
                "allow_negative_stock": True,
                "require_stock_reason": True,
                "default_vat_rate": 9,
            },
        )

        BrandingSettings.objects.get_or_create(
            company=company,
            defaults={
                "primary_color": "#111827",
                "accent_color": "#f59e0b",
                "background_color": "#f5f5f5",
                "text_color": "#222222",
                "card_color": "#ffffff",
                "public_title": "Restaurant De Molen",
                "font_family": "Arial, sans-serif",
            },
        )

        units = {
            "stuk": Unit.objects.get_or_create(name="Stuk", symbol="stuk", defaults={"unit_type": "piece", "decimal_places": 0})[0],
            "gram": Unit.objects.get_or_create(name="Gram", symbol="g", defaults={"unit_type": "weight", "decimal_places": 0})[0],
            "kilogram": Unit.objects.get_or_create(name="Kilogram", symbol="kg", defaults={"unit_type": "weight", "decimal_places": 3})[0],
            "liter": Unit.objects.get_or_create(name="Liter", symbol="l", defaults={"unit_type": "volume", "decimal_places": 3})[0],
            "milliliter": Unit.objects.get_or_create(name="Milliliter", symbol="ml", defaults={"unit_type": "volume", "decimal_places": 0})[0],
            "fles": Unit.objects.get_or_create(name="Fles", symbol="fles", defaults={"unit_type": "package", "decimal_places": 0})[0],
            "krat": Unit.objects.get_or_create(name="Krat", symbol="krat", defaults={"unit_type": "package", "decimal_places": 0})[0],
        }

        kitchen, _ = StockLocation.objects.get_or_create(
            name="Keuken",
            defaults={"description": "Hoofdlocatie voor ingrediënten.", "is_default": True},
        )
        StockLocation.objects.get_or_create(name="Bar", defaults={"description": "Voorraad achter de bar."})
        StockLocation.objects.get_or_create(name="Magazijn", defaults={"description": "Algemene opslag."})

        categories = {
            "gerechten": Category.objects.get_or_create(name="Gerechten", defaults={"sort_order": 10})[0],
            "dranken": Category.objects.get_or_create(name="Dranken", defaults={"sort_order": 20})[0],
            "ingredienten": Category.objects.get_or_create(name="Ingrediënten", defaults={"sort_order": 30})[0],
        }

        labels = {
            "populair": Label.objects.get_or_create(name="Populair")[0],
            "vegetarisch": Label.objects.get_or_create(name="Vegetarisch")[0],
        }

        kaas, _ = Item.objects.get_or_create(
            name="Jonge kaas",
            defaults={
                "item_type": "ingredient",
                "category": categories["ingredienten"],
                "description": "Kaas voor broodjes en tosti's.",
                "unit": units["gram"],
                "purchase_price": Decimal("0.0080"),
                "minimum_stock": Decimal("1000"),
                "is_stock_tracked": True,
                "status": "active",
            },
        )

        broodje, _ = Item.objects.get_or_create(
            name="Broodje",
            defaults={
                "item_type": "ingredient",
                "category": categories["ingredienten"],
                "description": "Basisbroodje voor lunchgerechten.",
                "unit": units["stuk"],
                "purchase_price": Decimal("0.3500"),
                "minimum_stock": Decimal("20"),
                "is_stock_tracked": True,
                "status": "active",
            },
        )

        tomaat, _ = Item.objects.get_or_create(
            name="Tomaat",
            defaults={
                "item_type": "ingredient",
                "category": categories["ingredienten"],
                "description": "Verse tomaat.",
                "unit": units["gram"],
                "purchase_price": Decimal("0.0040"),
                "minimum_stock": Decimal("1000"),
                "is_stock_tracked": True,
                "status": "active",
            },
        )

        cola, _ = Item.objects.get_or_create(
            name="Cola 330 ml",
            defaults={
                "item_type": "product",
                "category": categories["dranken"],
                "description": "Flesje cola.",
                "unit": units["stuk"],
                "sale_price": Decimal("2.75"),
                "purchase_price": Decimal("0.7000"),
                "minimum_stock": Decimal("24"),
                "is_stock_tracked": True,
                "is_featured": True,
                "status": "active",
            },
        )

        lunch, _ = Item.objects.get_or_create(
            name="Broodje gezond",
            defaults={
                "item_type": "menu_item",
                "category": categories["gerechten"],
                "description": "Vers broodje met kaas, tomaat en salade.",
                "unit": units["stuk"],
                "sale_price": Decimal("6.50"),
                "vat_rate": Decimal("9"),
                "is_stock_tracked": False,
                "is_featured": True,
                "status": "active",
            },
        )
        lunch.labels.add(labels["populair"])

        tosti, _ = Item.objects.get_or_create(
            name="Tosti kaas",
            defaults={
                "item_type": "menu_item",
                "category": categories["gerechten"],
                "description": "Tosti met jonge kaas.",
                "unit": units["stuk"],
                "sale_price": Decimal("4.95"),
                "vat_rate": Decimal("9"),
                "is_stock_tracked": False,
                "is_featured": True,
                "status": "active",
            },
        )
        tosti.labels.add(labels["vegetarisch"])

        lunch_recipe, _ = Recipe.objects.get_or_create(output_item=lunch, defaults={"servings": 1})
        RecipeIngredient.objects.get_or_create(recipe=lunch_recipe, ingredient=broodje, defaults={"quantity": Decimal("1")})
        RecipeIngredient.objects.get_or_create(recipe=lunch_recipe, ingredient=kaas, defaults={"quantity": Decimal("35")})
        RecipeIngredient.objects.get_or_create(recipe=lunch_recipe, ingredient=tomaat, defaults={"quantity": Decimal("50"), "waste_percentage": Decimal("5")})

        tosti_recipe, _ = Recipe.objects.get_or_create(output_item=tosti, defaults={"servings": 1})
        RecipeIngredient.objects.get_or_create(recipe=tosti_recipe, ingredient=broodje, defaults={"quantity": Decimal("2")})
        RecipeIngredient.objects.get_or_create(recipe=tosti_recipe, ingredient=kaas, defaults={"quantity": Decimal("50")})

        starting_stock = [
            (kaas, Decimal("5000"), "Startvoorraad kaas"),
            (broodje, Decimal("60"), "Startvoorraad broodjes"),
            (tomaat, Decimal("3000"), "Startvoorraad tomaten"),
            (cola, Decimal("48"), "Startvoorraad cola"),
        ]

        for item, quantity, reason in starting_stock:
            exists = StockMovement.objects.filter(item=item, movement_type="in", reason=reason).exists()
            if not exists:
                StockMovement.objects.create(
                    item=item,
                    location=kitchen,
                    movement_type="in",
                    quantity=quantity,
                    reason=reason,
                    note="Aangemaakt via demo seed.",
                )

        SetupState.objects.get_or_create(
            defaults={
                "is_completed": True,
                "completed_at": timezone.now(),
            }
        )

        self.stdout.write(self.style.SUCCESS("Restaurant demo is aangemaakt."))

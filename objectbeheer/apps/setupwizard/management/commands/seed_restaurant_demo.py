from decimal import Decimal

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
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
        company, _ = CompanyProfile.objects.update_or_create(
            name="Restaurant De Molen",
            defaults={
                "public_name": "Restaurant De Molen",
                "company_type": "restaurant",
                "email": "info@restaurantdemolen.test",
                "phone": "0123 456 789",
                "address": "Molenstraat 1, 1234 AB Voorbeeldstad",
            },
        )

        CompanySettings.objects.update_or_create(
            company=company,
            defaults={
                "enable_inventory": True,
                "enable_recipes": True,
                "enable_orders": False,
                "enable_public_catalog": True,
                "enable_prices": True,
                "enable_item_images": True,
                "enable_featured_items": True,
                "allow_negative_stock": True,
                "require_stock_reason": True,
                "default_vat_rate": Decimal("9"),
                "show_public_prices": True,
                "show_public_categories": True,
                "show_public_labels": True,
            },
        )

        BrandingSettings.objects.update_or_create(
            company=company,
            defaults={
                "primary_color": "#111827",
                "accent_color": "#f59e0b",
                "background_color": "#f8fafc",
                "text_color": "#172033",
                "muted_text_color": "#64748b",
                "card_color": "#ffffff",
                "border_color": "#e5e7eb",
                "public_title": "Restaurant De Molen",
                "font_family": "Inter, Arial, sans-serif",
                "show_images_by_default": True,
                "use_soft_shadows": True,
                "rounded_corners": 18,
                "max_page_width": 1180,
            },
        )

        stuk, _ = Unit.objects.update_or_create(
            symbol="stuk",
            defaults={
                "name": "Stuk",
                "unit_type": "piece",
                "base_unit": None,
                "factor_to_base": Decimal("1"),
                "decimal_places": 0,
                "is_active": True,
            },
        )

        gram, _ = Unit.objects.update_or_create(
            symbol="g",
            defaults={
                "name": "Gram",
                "unit_type": "weight",
                "base_unit": None,
                "factor_to_base": Decimal("1"),
                "decimal_places": 0,
                "is_active": True,
            },
        )

        kilogram, _ = Unit.objects.update_or_create(
            symbol="kg",
            defaults={
                "name": "Kilogram",
                "unit_type": "weight",
                "base_unit": gram,
                "factor_to_base": Decimal("1000"),
                "decimal_places": 3,
                "is_active": True,
            },
        )

        milliliter, _ = Unit.objects.update_or_create(
            symbol="ml",
            defaults={
                "name": "Milliliter",
                "unit_type": "volume",
                "base_unit": None,
                "factor_to_base": Decimal("1"),
                "decimal_places": 0,
                "is_active": True,
            },
        )

        centiliter, _ = Unit.objects.update_or_create(
            symbol="cl",
            defaults={
                "name": "Centiliter",
                "unit_type": "volume",
                "base_unit": milliliter,
                "factor_to_base": Decimal("10"),
                "decimal_places": 2,
                "is_active": True,
            },
        )

        liter, _ = Unit.objects.update_or_create(
            symbol="l",
            defaults={
                "name": "Liter",
                "unit_type": "volume",
                "base_unit": milliliter,
                "factor_to_base": Decimal("1000"),
                "decimal_places": 3,
                "is_active": True,
            },
        )

        fles, _ = Unit.objects.update_or_create(
            symbol="fles",
            defaults={
                "name": "Fles",
                "unit_type": "package",
                "base_unit": None,
                "factor_to_base": Decimal("1"),
                "decimal_places": 0,
                "is_active": True,
            },
        )

        krat, _ = Unit.objects.update_or_create(
            symbol="krat",
            defaults={
                "name": "Krat",
                "unit_type": "package",
                "base_unit": None,
                "factor_to_base": Decimal("1"),
                "decimal_places": 0,
                "is_active": True,
            },
        )

        keuken, _ = StockLocation.objects.update_or_create(
            name="Keuken",
            defaults={
                "description": "Hoofdlocatie voor ingrediënten.",
                "is_default": True,
                "is_active": True,
            },
        )

        StockLocation.objects.update_or_create(
            name="Bar",
            defaults={
                "description": "Voorraad achter de bar.",
                "is_active": True,
            },
        )

        StockLocation.objects.update_or_create(
            name="Magazijn",
            defaults={
                "description": "Algemene opslag.",
                "is_active": True,
            },
        )

        gerechten, _ = Category.objects.update_or_create(
            name="Gerechten",
            defaults={
                "sort_order": 10,
                "is_active": True,
            },
        )

        dranken, _ = Category.objects.update_or_create(
            name="Dranken",
            defaults={
                "sort_order": 20,
                "is_active": True,
            },
        )

        ingredienten, _ = Category.objects.update_or_create(
            name="Ingrediënten",
            defaults={
                "sort_order": 30,
                "is_active": True,
            },
        )

        populair, _ = Label.objects.get_or_create(name="Populair")
        vegetarisch, _ = Label.objects.get_or_create(name="Vegetarisch")

        kaas, _ = Item.objects.update_or_create(
            name="Jonge kaas",
            defaults={
                "item_type": "ingredient",
                "category": ingredienten,
                "short_description": "Kaas voor broodjes en tosti's.",
                "description": "Jonge kaas voor broodjes, tosti's en andere gerechten.",
                "unit": gram,
                "purchase_price": Decimal("0.0080"),
                "minimum_stock": Decimal("1000"),
                "is_stock_tracked": True,
                "show_image": False,
                "status": "active",
            },
        )

        broodje, _ = Item.objects.update_or_create(
            name="Broodje",
            defaults={
                "item_type": "ingredient",
                "category": ingredienten,
                "short_description": "Basisbroodje voor lunchgerechten.",
                "description": "Basisbroodje voor lunchgerechten.",
                "unit": stuk,
                "purchase_price": Decimal("0.3500"),
                "minimum_stock": Decimal("20"),
                "is_stock_tracked": True,
                "show_image": False,
                "status": "active",
            },
        )

        tomaat, _ = Item.objects.update_or_create(
            name="Tomaat",
            defaults={
                "item_type": "ingredient",
                "category": ingredienten,
                "short_description": "Verse tomaat.",
                "description": "Verse tomaat voor broodjes en salades.",
                "unit": gram,
                "purchase_price": Decimal("0.0040"),
                "minimum_stock": Decimal("1000"),
                "is_stock_tracked": True,
                "show_image": False,
                "status": "active",
            },
        )

        cola, _ = Item.objects.update_or_create(
            name="Cola 330 ml",
            defaults={
                "item_type": "product",
                "category": dranken,
                "short_description": "Fris en koud geserveerd.",
                "description": "Flesje cola van 330 milliliter.",
                "unit": stuk,
                "sale_price": Decimal("2.75"),
                "purchase_price": Decimal("0.7000"),
                "minimum_stock": Decimal("24"),
                "is_stock_tracked": True,
                "show_image": True,
                "use_default_image_when_missing": True,
                "is_featured": True,
                "status": "active",
            },
        )

        lunch, _ = Item.objects.update_or_create(
            name="Broodje gezond",
            defaults={
                "item_type": "menu_item",
                "category": gerechten,
                "short_description": "Vers broodje met kaas, tomaat en salade.",
                "description": "Een vers broodje met jonge kaas, tomaat en frisse salade.",
                "unit": stuk,
                "sale_price": Decimal("6.50"),
                "vat_rate": Decimal("9"),
                "is_stock_tracked": False,
                "show_image": True,
                "use_default_image_when_missing": True,
                "is_featured": True,
                "status": "active",
            },
        )
        lunch.labels.add(populair)

        tosti, _ = Item.objects.update_or_create(
            name="Tosti kaas",
            defaults={
                "item_type": "menu_item",
                "category": gerechten,
                "short_description": "Knapperige tosti met jonge kaas.",
                "description": "Een warme tosti met jonge kaas.",
                "unit": stuk,
                "sale_price": Decimal("4.95"),
                "vat_rate": Decimal("9"),
                "is_stock_tracked": False,
                "show_image": True,
                "use_default_image_when_missing": True,
                "is_featured": True,
                "status": "active",
            },
        )
        tosti.labels.add(vegetarisch)

        lunch_recipe, _ = Recipe.objects.get_or_create(
            output_item=lunch,
            defaults={
                "servings": 1,
            },
        )

        RecipeIngredient.objects.update_or_create(
            recipe=lunch_recipe,
            ingredient=broodje,
            defaults={
                "quantity": Decimal("1"),
            },
        )

        RecipeIngredient.objects.update_or_create(
            recipe=lunch_recipe,
            ingredient=kaas,
            defaults={
                "quantity": Decimal("35"),
            },
        )

        RecipeIngredient.objects.update_or_create(
            recipe=lunch_recipe,
            ingredient=tomaat,
            defaults={
                "quantity": Decimal("50"),
                "waste_percentage": Decimal("5"),
            },
        )

        tosti_recipe, _ = Recipe.objects.get_or_create(
            output_item=tosti,
            defaults={
                "servings": 1,
            },
        )

        RecipeIngredient.objects.update_or_create(
            recipe=tosti_recipe,
            ingredient=broodje,
            defaults={
                "quantity": Decimal("2"),
            },
        )

        RecipeIngredient.objects.update_or_create(
            recipe=tosti_recipe,
            ingredient=kaas,
            defaults={
                "quantity": Decimal("50"),
            },
        )

        starting_stock = [
            (kaas, Decimal("5000"), gram, "Startvoorraad kaas"),
            (broodje, Decimal("60"), stuk, "Startvoorraad broodjes"),
            (tomaat, Decimal("3000"), gram, "Startvoorraad tomaten"),
            (cola, Decimal("48"), stuk, "Startvoorraad cola"),
        ]

        for item, quantity, unit, reason in starting_stock:
            exists = StockMovement.objects.filter(
                item=item,
                movement_type="in",
                reason=reason,
            ).exists()

            if not exists:
                StockMovement.objects.create(
                    item=item,
                    location=keuken,
                    movement_type="in",
                    quantity=quantity,
                    unit=unit,
                    reason_code="purchase",
                    reason=reason,
                    note="Aangemaakt via demo seed.",
                )

        SetupState.objects.update_or_create(
            id=1,
            defaults={
                "is_completed": True,
                "completed_at": timezone.now(),
            },
        )

        stock_content_type = ContentType.objects.get_for_model(StockMovement)

        stock_permissions = Permission.objects.filter(
            content_type=stock_content_type,
            codename__in=[
                "can_adjust_stock",
                "can_view_stock_dashboard",
                "view_stockmovement",
                "add_stockmovement",
            ],
        )

        medewerker_group, _ = Group.objects.get_or_create(name="Medewerker")
        voorraad_group, _ = Group.objects.get_or_create(name="Voorraadbeheerder")
        manager_group, _ = Group.objects.get_or_create(name="Manager")

        medewerker_group.permissions.add(
            *stock_permissions.filter(
                codename__in=[
                    "can_view_stock_dashboard",
                    "view_stockmovement",
                ]
            )
        )

        voorraad_group.permissions.add(*stock_permissions)
        manager_group.permissions.add(*stock_permissions)


        item_content_type = ContentType.objects.get_for_model(Item)

        item_permissions = Permission.objects.filter(
            content_type=item_content_type,
            codename__in=[
                "view_item",
                "add_item",
                "change_item",
                "view_category",
                "add_category",
                "change_category",
                "view_label",
                "add_label",
                "change_label",
            ],
        )

        medewerker_group.permissions.add(
            *item_permissions.filter(codename__in=["view_item", "view_category", "view_label"])
        )
        voorraad_group.permissions.add(*item_permissions)
        manager_group.permissions.add(*item_permissions)

        self.stdout.write(self.style.SUCCESS("Restaurant demo is bijgewerkt."))

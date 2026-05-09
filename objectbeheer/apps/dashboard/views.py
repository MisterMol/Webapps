from django.shortcuts import redirect, render

from apps.company.models import CompanyProfile
from apps.inventory.models import StockMovement
from apps.items.models import Item
from apps.recipes.models import Recipe


PUBLIC_MENU_TYPES = ["menu_item", "drink", "product"]


def public_menu_queryset():
    return (
        Item.objects
        .filter(
            status="active",
            item_type__in=PUBLIC_MENU_TYPES,
            media_files__is_public=True,
        )
        .select_related("category", "unit")
        .prefetch_related("media_files", "labels")
        .distinct()
    )


def home(request):
    if not CompanyProfile.objects.exists():
        return redirect("setupwizard:start")

    featured_items = (
        public_menu_queryset()
        .filter(is_featured=True)
        .order_by("category__sort_order", "category__name", "name")[:6]
    )

    public_items = (
        public_menu_queryset()
        .order_by("category__sort_order", "category__name", "name")[:12]
    )

    return render(
        request,
        "public/home.html",
        {
            "featured_items": featured_items,
            "public_items": public_items,
        },
    )


def dashboard_home(request):
    item_count = Item.objects.count()
    active_item_count = Item.objects.filter(status="active").count()
    recipe_count = Recipe.objects.count()
    stock_movement_count = StockMovement.objects.count()
    recent_movements = (
        StockMovement.objects
        .select_related("item", "location")
        .order_by("-created_at")[:10]
    )

    return render(
        request,
        "dashboard/home.html",
        {
            "item_count": item_count,
            "active_item_count": active_item_count,
            "recipe_count": recipe_count,
            "stock_movement_count": stock_movement_count,
            "recent_movements": recent_movements,
        },
    )

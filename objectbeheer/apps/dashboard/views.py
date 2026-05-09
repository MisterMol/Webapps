from django.shortcuts import redirect, render

from apps.company.models import CompanyProfile
from apps.inventory.models import StockMovement
from apps.items.models import Item
from apps.recipes.models import Recipe


def home(request):
    if not CompanyProfile.objects.exists():
        return redirect("setupwizard:start")

    featured_items = (
        Item.objects
        .filter(status="active", is_featured=True)
        .select_related("category", "unit")
        .prefetch_related("media_files", "labels")[:6]
    )

    public_items = (
        Item.objects
        .filter(status="active")
        .select_related("category", "unit")
        .prefetch_related("media_files", "labels")[:12]
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
        .select_related("item", "location", "unit")
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

from django.shortcuts import redirect, render

from apps.company.models import CompanyProfile
from apps.inventory.models import StockMovement, item_is_available
from apps.items.models import Item
from apps.items.services.sorting import horeca_sort_key
from apps.recipes.models import Recipe


PUBLIC_MENU_TYPES = ["menu_item", "drink", "product"]


def public_menu_queryset():
    return (
        Item.objects
        .filter(
            status="active",
            item_type__in=PUBLIC_MENU_TYPES,
        )
        .select_related("category", "unit")
        .prefetch_related("media_files", "labels", "stock_movements")
        .distinct()
    )


def get_available_public_items(limit=None, featured_only=False):
    queryset = public_menu_queryset()

    if featured_only:
        queryset = queryset.filter(is_featured=True)

    rows = []

    for item in queryset:
        if item_is_available(item):
            rows.append({"item": item})

    rows = sorted(rows, key=horeca_sort_key)
    items = [row["item"] for row in rows]

    if limit:
        return items[:limit]

    return items


def home(request):
    if not CompanyProfile.objects.exists():
        return redirect("setupwizard:start")

    featured_items = get_available_public_items(limit=6, featured_only=True)
    public_items = get_available_public_items(limit=12)

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

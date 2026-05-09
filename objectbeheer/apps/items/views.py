from django.shortcuts import get_object_or_404, render

from .models import Category, Item


def public_item_list(request):
    categories = Category.objects.filter(is_active=True)
    items = (
        Item.objects
        .filter(status="active")
        .select_related("category", "unit")
        .prefetch_related("images", "labels")
        .order_by("category__sort_order", "category__name", "name")
    )

    category_slug = request.GET.get("categorie")
    if category_slug:
        items = items.filter(category__slug=category_slug)

    return render(
        request,
        "items/public_item_list.html",
        {
            "categories": categories,
            "items": items,
            "selected_category": category_slug,
        },
    )


def public_item_detail(request, slug):
    item = get_object_or_404(
        Item.objects.filter(status="active").select_related("category", "unit").prefetch_related("images", "labels"),
        slug=slug,
    )

    return render(
        request,
        "items/public_item_detail.html",
        {
            "item": item,
        },
    )


def dashboard_item_list(request):
    items = Item.objects.select_related("category", "unit").prefetch_related("images").all()
    return render(request, "items/dashboard_item_list.html", {"items": items})

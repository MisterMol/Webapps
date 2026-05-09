from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.items.models import Item
from .models import StockLocation, calculate_stock


@login_required
def inventory_overview(request):
    items = Item.objects.filter(is_stock_tracked=True).select_related("unit", "category")
    locations = StockLocation.objects.filter(is_active=True)

    rows = []
    for item in items:
        rows.append(
            {
                "item": item,
                "stock": calculate_stock(item),
            }
        )

    return render(
        request,
        "inventory/overview.html",
        {
            "rows": rows,
            "locations": locations,
        },
    )

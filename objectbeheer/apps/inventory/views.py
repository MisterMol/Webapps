from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect, render

from apps.items.models import Item

from .forms import StockAdjustmentForm
from .models import StockLocation, StockMovement, calculate_stock, item_is_available
from .services import apply_stock_action


@login_required
def public_inventory_map(request):
    items = (
        Item.objects
        .filter(status="active", is_stock_tracked=True)
        .select_related("unit", "category")
        .prefetch_related("media_files", "labels")
        .order_by("category__sort_order", "category__name", "name")
    )

    rows = []

    for item in items:
        stock = calculate_stock(item)

        if stock <= Decimal("0"):
            continue

        rows.append(
            {
                "item": item,
                "stock": stock,
                "available": item_is_available(item),
            }
        )

    return render(
        request,
        "inventory/public_inventory_map.html",
        {
            "rows": rows,
        },
    )


@login_required
@permission_required("inventory.can_view_stock_dashboard", raise_exception=True)
def inventory_overview(request):
    items = Item.objects.filter(is_stock_tracked=True).select_related("unit", "category")
    locations = StockLocation.objects.filter(is_active=True)

    rows = []

    for item in items:
        stock = calculate_stock(item)
        is_low = False

        if item.minimum_stock is not None:
            is_low = stock <= item.minimum_stock

        rows.append(
            {
                "item": item,
                "stock": stock,
                "is_low": is_low,
                "available": stock > Decimal("0"),
            }
        )

    recent_movements = (
        StockMovement.objects
        .select_related("item", "location", "unit", "created_by")
        .order_by("-created_at")[:40]
    )

    return render(
        request,
        "inventory/overview.html",
        {
            "rows": rows,
            "locations": locations,
            "recent_movements": recent_movements,
        },
    )


@login_required
@permission_required("inventory.can_adjust_stock", raise_exception=True)
def stock_movement_create(request):
    if request.method == "POST":
        form = StockAdjustmentForm(request.POST)

        if form.is_valid():
            movement = apply_stock_action(
                item=form.cleaned_data["item"],
                action=form.cleaned_data["action"],
                quantity=form.cleaned_data.get("quantity"),
                counted_quantity=form.cleaned_data.get("counted_quantity"),
                user=request.user,
                location=form.cleaned_data["location"],
                reason_code=form.cleaned_data.get("reason_code"),
                note=form.cleaned_data.get("note", ""),
            )

            if movement:
                messages.success(
                    request,
                    f"Voorraad is bijgewerkt voor {movement.item.name}."
                )
            else:
                messages.success(
                    request,
                    "Voorraadtelling opgeslagen. Er was geen verschil met de huidige voorraad."
                )

            return redirect("inventory:overview")
    else:
        form = StockAdjustmentForm()

    recent_movements = (
        StockMovement.objects
        .select_related("item", "location", "unit", "created_by")
        .order_by("-created_at")[:15]
    )

    items = (
        Item.objects
        .filter(is_stock_tracked=True, status="active")
        .select_related("unit", "category")
        .order_by("name")
    )

    item_status_map = {}

    for item in items:
        latest_movements = (
            item.stock_movements
            .select_related("location", "unit", "created_by")
            .order_by("-created_at")[:10]
        )

        item_status_map[str(item.id)] = {
            "name": item.name,
            "unit": item.unit.symbol if item.unit else "",
            "stock": str(calculate_stock(item)),
            "minimum_stock": str(item.minimum_stock) if item.minimum_stock is not None else "",
            "mutations": [
                {
                    "created_at": movement.created_at.strftime("%d-%m-%Y %H:%M"),
                    "movement_type": movement.get_movement_type_display(),
                    "direction": movement.direction_label,
                    "signed_quantity": str(movement.signed_quantity),
                    "quantity": str(movement.quantity),
                    "unit": str(movement.effective_unit or ""),
                    "reason": movement.get_reason_code_display(),
                    "user": str(movement.created_by or "Systeem"),
                    "note": movement.note,
                }
                for movement in latest_movements
            ],
        }

    return render(
        request,
        "inventory/stock_movement_form.html",
        {
            "form": form,
            "recent_movements": recent_movements,
            "item_status_map": item_status_map,
        },
    )

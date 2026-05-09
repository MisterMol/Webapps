from decimal import Decimal

from django.db import transaction

from apps.auditlog.services import write_audit_log

from .models import StockLocation, StockMovement, calculate_stock


ACTION_TO_MOVEMENT = {
    "purchase": ("purchase", "purchase"),
    "return": ("return", "return"),
    "stock_in": ("in", "correction_plus"),
    "stock_out": ("out", "correction_minus"),
    "sale": ("sale", "sale"),
    "waste": ("waste", "waste"),
    "expired": ("expired", "expired"),
    "breakage": ("breakage", "breakage"),
    "donation": ("donation", "donation"),
    "internal_use": ("internal_use", "internal_use"),
}


def get_default_location():
    location = StockLocation.objects.filter(is_default=True, is_active=True).first()

    if location:
        return location

    return StockLocation.objects.filter(is_active=True).first()


@transaction.atomic
def book_stock(
    item,
    movement_type,
    quantity,
    user=None,
    location=None,
    unit=None,
    reason_code="other",
    reason="",
    note="",
):
    if location is None:
        location = get_default_location()

    if location is None:
        raise ValueError("Er is geen voorraadlocatie beschikbaar.")

    if unit is None:
        unit = item.unit

    movement = StockMovement.objects.create(
        item=item,
        location=location,
        movement_type=movement_type,
        quantity=quantity,
        unit=unit,
        reason_code=reason_code,
        reason=reason,
        note=note,
        created_by=user,
    )

    write_audit_log(
        action="inventory.stock_movement_created",
        user=user,
        obj=movement,
        message=(
            f"Voorraadmutatie voor {item.name}: "
            f"{movement.direction_label} met {quantity} {unit or item.unit}. "
            f"Actie: {movement.get_movement_type_display()}. "
            f"Reden: {movement.get_reason_code_display()}."
        ),
        new_value={
            "item": item.name,
            "movement_type": movement_type,
            "direction": movement.direction_label,
            "quantity": str(quantity),
            "unit": str(unit or item.unit),
            "reason_code": reason_code,
            "reason": reason,
            "note": note,
            "location": str(location),
            "stock_after": str(calculate_stock(item)),
        },
    )

    return movement


@transaction.atomic
def apply_stock_action(
    item,
    action,
    quantity=None,
    counted_quantity=None,
    user=None,
    location=None,
    reason_code=None,
    note="",
):
    if action == "stock_count":
        return apply_stock_count(
            item=item,
            counted_quantity=counted_quantity,
            user=user,
            location=location,
            note=note,
        )

    if action not in ACTION_TO_MOVEMENT:
        raise ValueError("Onbekende voorraadactie.")

    movement_type, default_reason_code = ACTION_TO_MOVEMENT[action]

    return book_stock(
        item=item,
        movement_type=movement_type,
        quantity=quantity,
        user=user,
        location=location,
        unit=item.unit,
        reason_code=reason_code or default_reason_code,
        reason="Handmatige voorraadmutatie",
        note=note,
    )


@transaction.atomic
def apply_stock_count(item, counted_quantity, user=None, location=None, note=""):
    counted_quantity = Decimal(str(counted_quantity))
    current_stock = calculate_stock(item, location=location)
    difference = counted_quantity - current_stock

    if difference == 0:
        write_audit_log(
            action="inventory.stock_count_no_change",
            user=user,
            obj=item,
            message=f"Voorraadtelling voor {item.name}: geen verschil. Geteld: {counted_quantity}.",
            new_value={
                "item": item.name,
                "counted_quantity": str(counted_quantity),
                "current_stock": str(current_stock),
                "difference": "0",
                "unit": str(item.unit),
                "location": str(location or get_default_location()),
                "note": note,
            },
        )
        return None

    if difference > 0:
        movement_type = "correction_in"
        reason_code = "manual_count_plus"
        quantity = difference
    else:
        movement_type = "correction_out"
        reason_code = "manual_count_minus"
        quantity = abs(difference)

    movement = book_stock(
        item=item,
        movement_type=movement_type,
        quantity=quantity,
        user=user,
        location=location,
        unit=item.unit,
        reason_code=reason_code,
        reason="Voorraadtelling",
        note=(
            f"Getelde voorraad: {counted_quantity} {item.unit}. "
            f"Voor telling: {current_stock} {item.unit}. "
            f"Verschil: {difference} {item.unit}. "
            f"{note}".strip()
        ),
    )

    write_audit_log(
        action="inventory.stock_count_applied",
        user=user,
        obj=movement,
        message=f"Voorraadtelling toegepast voor {item.name}. Geteld: {counted_quantity}. Verschil: {difference}.",
        new_value={
            "item": item.name,
            "counted_quantity": str(counted_quantity),
            "previous_stock": str(current_stock),
            "difference": str(difference),
            "unit": str(item.unit),
            "movement_id": movement.id,
        },
    )

    return movement

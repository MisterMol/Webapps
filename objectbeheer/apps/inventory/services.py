from django.db import transaction

from .models import StockLocation, StockMovement


def get_default_location():
    location = StockLocation.objects.filter(is_default=True, is_active=True).first()

    if location:
        return location

    return StockLocation.objects.filter(is_active=True).first()


@transaction.atomic
def book_stock(item, movement_type, quantity, user=None, location=None, reason="", note=""):
    if location is None:
        location = get_default_location()

    if location is None:
        raise ValueError("Er is geen voorraadlocatie beschikbaar.")

    return StockMovement.objects.create(
        item=item,
        location=location,
        movement_type=movement_type,
        quantity=quantity,
        reason=reason,
        note=note,
        created_by=user,
    )

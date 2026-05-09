from decimal import Decimal, InvalidOperation

from django import template


register = template.Library()


@register.filter
def smart_quantity(value):
    if value is None:
        return ""

    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return value

    if number == number.to_integral():
        return str(number.quantize(Decimal("1")))

    normalized = number.normalize()
    text = format(normalized, "f")

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text.replace(".", ",")


@register.filter
def signed_class(value):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return ""

    if number < 0:
        return "negative"

    if number > 0:
        return "positive"

    return "neutral"


@register.filter
def signed_prefix(value):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return ""

    if number < 0:
        return "-"

    if number > 0:
        return "+"

    return ""

from decimal import Decimal

from django import forms

from apps.items.models import Item

from .models import StockLocation


class StockAdjustmentForm(forms.Form):
    ACTION_CHOICES = [
        ("purchase", "Inkoop"),
        ("return", "Retour erbij"),
        ("stock_in", "Voorraad erbij"),
        ("stock_out", "Voorraad eraf"),
        ("sale", "Verkoop"),
        ("waste", "Derving"),
        ("expired", "Over datum"),
        ("breakage", "Breuk of schade"),
        ("donation", "Donatie"),
        ("internal_use", "Intern gebruik"),
        ("stock_count", "Voorraadtelling"),
    ]

    REASON_CHOICES = [
        ("purchase", "Inkoop"),
        ("return", "Retour"),
        ("correction_plus", "Correctie erbij"),
        ("correction_minus", "Correctie eraf"),
        ("sale", "Verkoop"),
        ("waste", "Derving"),
        ("expired", "Over datum"),
        ("breakage", "Breuk of schade"),
        ("donation", "Donatie"),
        ("internal_use", "Intern gebruik"),
        ("manual_count", "Voorraadtelling"),
        ("other", "Overig"),
    ]

    item = forms.ModelChoiceField(
        label="Item",
        queryset=Item.objects.none(),
    )
    location = forms.ModelChoiceField(
        label="Voorraadlocatie",
        queryset=StockLocation.objects.none(),
    )
    action = forms.ChoiceField(
        label="Actie",
        choices=ACTION_CHOICES,
    )
    quantity = forms.DecimalField(
        label="Hoeveelheid",
        required=False,
        max_digits=12,
        decimal_places=3,
        min_value=Decimal("0.001"),
        help_text="Gebruik dit voor inkoop, afboeken, derving, donatie enzovoort.",
    )
    counted_quantity = forms.DecimalField(
        label="Getelde voorraad",
        required=False,
        max_digits=12,
        decimal_places=3,
        min_value=Decimal("0"),
        help_text="Alleen gebruiken bij voorraadtelling. Vul in wat je echt hebt geteld.",
    )
    reason_code = forms.ChoiceField(
        label="Reden",
        choices=REASON_CHOICES,
    )
    note = forms.CharField(
        label="Toelichting",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["item"].queryset = (
            Item.objects
            .filter(is_stock_tracked=True, status="active")
            .select_related("unit", "category")
            .order_by("name")
        )
        self.fields["location"].queryset = StockLocation.objects.filter(is_active=True).order_by("name")

    def clean(self):
        cleaned_data = super().clean()

        action = cleaned_data.get("action")
        reason_code = cleaned_data.get("reason_code")
        quantity = cleaned_data.get("quantity")
        counted_quantity = cleaned_data.get("counted_quantity")

        allowed_reasons = {
            "purchase": ["purchase"],
            "return": ["return"],
            "stock_in": ["correction_plus", "other"],
            "stock_out": ["correction_minus", "other"],
            "sale": ["sale"],
            "waste": ["waste"],
            "expired": ["expired"],
            "breakage": ["breakage"],
            "donation": ["donation"],
            "internal_use": ["internal_use"],
            "stock_count": ["manual_count"],
        }

        if action and reason_code not in allowed_reasons.get(action, []):
            raise forms.ValidationError("Deze reden hoort niet bij deze actie.")

        if action == "stock_count":
            if counted_quantity is None:
                raise forms.ValidationError("Vul de getelde voorraad in.")
        else:
            if quantity is None:
                raise forms.ValidationError("Vul een hoeveelheid in.")

        return cleaned_data

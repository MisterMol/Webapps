from django import forms

from apps.items.models import Item

from .models import Recipe, RecipeIngredient


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ["servings", "instructions", "is_active"]
        widgets = {
            "instructions": forms.Textarea(attrs={"rows": 4}),
        }
        help_texts = {
            "servings": "Aantal porties of verkoopitems waarvoor deze receptuur geldt. Meestal 1.",
            "instructions": "Interne bereidingswijze of opmerkingen voor medewerkers.",
            "is_active": "Alleen actieve recepten worden gebruikt voor beschikbaarheid en voorraadverbruik.",
        }


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ["ingredient", "quantity", "waste_percentage", "is_optional", "note"]
        help_texts = {
            "ingredient": "Kies welk ingrediënt nodig is.",
            "quantity": "Hoeveel van dit ingrediënt nodig is voor de receptuur.",
            "waste_percentage": "Extra marge voor verlies, snijverlies of morsen. Laat op 0 als je dit niet nodig hebt.",
            "is_optional": "Zet dit aan als het ingrediënt mag ontbreken. Bijvoorbeeld cocktailkers of extra garnering.",
            "note": "Bijvoorbeeld: mag wegblijven, extra bij luxe variant, of alleen op verzoek.",
        }

    def __init__(self, *args, **kwargs):
        recipe = kwargs.pop("recipe", None)
        super().__init__(*args, **kwargs)

        self.fields["ingredient"].queryset = (
            Item.objects
            .filter(status="active", is_stock_tracked=True)
            .exclude(id=recipe.output_item_id if recipe else None)
            .select_related("unit", "category")
            .order_by("category__name", "name")
        )

        self.fields["ingredient"].label = "Ingrediënt"
        self.fields["quantity"].label = "Hoeveelheid"
        self.fields["waste_percentage"].label = "Marge of verliespercentage"
        self.fields["is_optional"].label = "Optioneel ingrediënt"
        self.fields["note"].label = "Notitie"
        self.fields["note"].required = False

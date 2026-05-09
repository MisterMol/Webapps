from decimal import Decimal
from pathlib import Path

from django import forms

from apps.inventory.models import StockLocation, Unit

from .models import Allergen, Category, Item, Label


ALLOWED_MEDIA_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".avif",
    ".svg",
    ".gif",
    ".mp4",
    ".webm",
    ".mov",
}


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={"multiple": True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if not data:
            return []

        if not isinstance(data, (list, tuple)):
            data = [data]

        cleaned_files = []

        for uploaded_file in data:
            cleaned_files.append(super().clean(uploaded_file, initial))

        return cleaned_files


class ItemCreateForm(forms.ModelForm):
    media_files = MultipleFileField(
        label="Afbeeldingen, gifjes of video’s",
        required=False,
        help_text="Je kunt meerdere bestanden kiezen. Toegestaan: jpg, png, webp, gif, mp4, webm en mov.",
    )

    initial_stock_quantity = forms.DecimalField(
        label="Directe inkoopvoorraad",
        required=False,
        max_digits=12,
        decimal_places=3,
        min_value=Decimal("0"),
        help_text="Gebruik dit als je het item meteen op voorraad wilt zetten. Bijvoorbeeld 48 kroketten.",
    )
    initial_stock_location = forms.ModelChoiceField(
        label="Voorraadlocatie",
        required=False,
        queryset=StockLocation.objects.none(),
        help_text="Waar ligt deze voorraad? Bijvoorbeeld keuken, bar of magazijn.",
    )
    initial_stock_unit = forms.ModelChoiceField(
        label="Voorraadeenheid",
        required=False,
        queryset=Unit.objects.none(),
        help_text="Laat leeg om de vaste eenheid van het item te gebruiken.",
    )
    initial_stock_note = forms.CharField(
        label="Toelichting startvoorraad",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Bijvoorbeeld: Eerste levering, factuur 2026-001 of handmatige startvoorraad.",
    )

    class Meta:
        model = Item
        fields = [
            "item_type",
            "name",
            "sku",
            "category",
            "labels",
            "allergens",
            "short_description",
            "description",
            "unit",
            "sale_price",
            "purchase_price",
            "vat_rate",
            "minimum_stock",
            "is_stock_tracked",
            "show_image",
            "use_default_image_when_missing",
            "is_featured",
            "status",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "short_description": forms.TextInput(),
            "labels": forms.CheckboxSelectMultiple(),
            "allergens": forms.CheckboxSelectMultiple(),
        }
        help_texts = {
            "item_type": "Kies wat je aanmaakt. Een ingrediënt is iets dat je gebruikt in recepten. Een product of drank kan direct verkocht of getoond worden.",
            "name": "De naam die medewerkers en bezoekers zien. Bijvoorbeeld Kroket, Cola 330 ml of Broodje gezond.",
            "sku": "Optioneel intern artikelnummer. Handig als je later importeert, exporteert of leverancierscodes gebruikt.",
            "category": "Categorie bepaalt waar het item onder valt. Bijvoorbeeld Dranken, Ingrediënten of Gerechten.",
            "labels": "Labels zijn extra kenmerken zoals Populair, Vegetarisch, Pittig of Alcoholvrij. Je kunt meerdere labels kiezen.",
            "allergens": "Kies allergenen die direct in dit item zitten. Bij gerechten worden allergenen van ingrediënten later ook meegenomen.",
            "short_description": "Korte tekst voor kaarten en overzichten. Houd dit kort en duidelijk.",
            "description": "Langere omschrijving voor de detailpagina.",
            "unit": "De vaste eenheid waarin je voorraad telt. Bijvoorbeeld stuk, gram, kilogram, liter of milliliter.",
            "sale_price": "Verkoopprijs voor klanten. Laat leeg als je geen prijs wilt tonen of als het alleen een ingrediënt is.",
            "purchase_price": "Inkoopprijs per vaste eenheid. Bijvoorbeeld per stuk, per gram of per liter.",
            "vat_rate": "Voor horeca is 9 procent vaak van toepassing op eten en non-alcoholische dranken. Alcohol is vaak 21 procent. Controleer dit altijd zelf.",
            "minimum_stock": "Onder deze voorraad wordt het item als lage voorraad gemarkeerd.",
            "is_stock_tracked": "Zet dit aan als je voorraad wilt bijhouden. Voor kroketten, cola, kaas en tomaten dus wel. Voor een dienst meestal niet.",
            "show_image": "Zet dit uit als je geen afbeelding of media wilt tonen voor dit item.",
            "use_default_image_when_missing": "Als er geen eigen afbeelding is, gebruikt de site de standaardafbeelding uit branding.",
            "is_featured": "Toon dit item op plekken zoals de homepagina of uitgelichte items.",
            "status": "Alleen actieve items zijn publiek zichtbaar. Concept is handig als je nog bezig bent.",
        }

    def __init__(self, *args, item_type=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["category"].queryset = Category.objects.filter(is_active=True).order_by("sort_order", "name")
        self.fields["labels"].queryset = Label.objects.order_by("name")
        self.fields["allergens"].queryset = Allergen.objects.filter(is_active=True).order_by("name")
        self.fields["unit"].queryset = Unit.objects.filter(is_active=True).order_by("unit_type", "name")
        self.fields["initial_stock_location"].queryset = StockLocation.objects.filter(is_active=True).order_by("name")
        self.fields["initial_stock_unit"].queryset = Unit.objects.filter(is_active=True).order_by("unit_type", "name")

        self.fields["item_type"].label = "Wat wil je toevoegen?"
        self.fields["name"].label = "Naam"
        self.fields["sku"].label = "Artikelcode"
        self.fields["category"].label = "Categorie"
        self.fields["labels"].label = "Labels"
        self.fields["allergens"].label = "Allergenen"
        self.fields["short_description"].label = "Korte omschrijving"
        self.fields["description"].label = "Omschrijving"
        self.fields["unit"].label = "Vaste eenheid"
        self.fields["sale_price"].label = "Verkoopprijs"
        self.fields["purchase_price"].label = "Inkoopprijs per eenheid"
        self.fields["vat_rate"].label = "Btw percentage"
        self.fields["minimum_stock"].label = "Minimumvoorraad"
        self.fields["is_stock_tracked"].label = "Voorraad bijhouden"
        self.fields["show_image"].label = "Media tonen"
        self.fields["use_default_image_when_missing"].label = "Standaardafbeelding gebruiken als er geen media is"
        self.fields["is_featured"].label = "Uitgelicht tonen"
        self.fields["status"].label = "Status"

        media_choices = []
        if self.instance and self.instance.pk:
            media_files = self.instance.media_files.filter(is_public=True).order_by("sort_order", "uploaded_at", "id")
            media_choices = [
                (str(media.id), media.caption or media.alt_text or media.image.name)
                for media in media_files
            ]

            primary_media = media_files.filter(is_primary=True).first()
            if primary_media:
                self.fields["primary_media_id"].initial = str(primary_media.id)
            elif media_files.count() == 1:
                self.fields["primary_media_id"].initial = str(media_files.first().id)

        self.fields["primary_media_id"].choices = media_choices

        self.fields["labels"].required = False
        self.fields["allergens"].required = False
        self.fields["sku"].required = False
        self.fields["short_description"].required = False
        self.fields["description"].required = False
        self.fields["sale_price"].required = False
        self.fields["purchase_price"].required = False
        self.fields["minimum_stock"].required = False

        if item_type:
            self.fields["item_type"].initial = item_type

            if item_type == "ingredient":
                self.fields["is_stock_tracked"].initial = True
                self.fields["show_image"].initial = False

            if item_type in ["product", "drink"]:
                self.fields["is_stock_tracked"].initial = True
                self.fields["show_image"].initial = True

            if item_type == "menu_item":
                self.fields["is_stock_tracked"].initial = False
                self.fields["show_image"].initial = True
                self.fields["is_featured"].initial = True

    def clean_media_files(self):
        files = self.cleaned_data.get("media_files", [])

        for uploaded_file in files:
            suffix = Path(uploaded_file.name).suffix.lower()

            if suffix not in ALLOWED_MEDIA_EXTENSIONS:
                raise forms.ValidationError(
                    f"{uploaded_file.name} heeft een niet toegestaan bestandstype."
                )

            if uploaded_file.size > 25 * 1024 * 1024:
                raise forms.ValidationError(
                    f"{uploaded_file.name} is groter dan 25 MB."
                )

        return files

    def clean(self):
        cleaned_data = super().clean()

        is_stock_tracked = cleaned_data.get("is_stock_tracked")
        unit = cleaned_data.get("unit")
        initial_stock_quantity = cleaned_data.get("initial_stock_quantity")
        initial_stock_location = cleaned_data.get("initial_stock_location")

        if is_stock_tracked and not unit:
            raise forms.ValidationError("Kies een vaste eenheid als je voorraad wilt bijhouden.")

        if initial_stock_quantity and not is_stock_tracked:
            raise forms.ValidationError("Zet 'Voorraad bijhouden' aan als je directe inkoopvoorraad invult.")

        if initial_stock_quantity and not initial_stock_location:
            raise forms.ValidationError("Kies een voorraadlocatie voor de directe inkoopvoorraad.")

        return cleaned_data


class ItemUpdateForm(forms.ModelForm):
    primary_media_id = forms.ChoiceField(
        label="Hoofdafbeelding",
        required=False,
        help_text="Kies welke afbeelding standaard zichtbaar is op kaarten en detailpagina’s.",
    )

    media_files = MultipleFileField(
        label="Nieuwe afbeeldingen, gifjes of video’s toevoegen",
        required=False,
        help_text="Upload extra media voor dit item. Bestaande media blijft staan. Toegestaan: jpg, png, webp, gif, mp4, webm en mov.",
    )

    class Meta:
        model = Item
        fields = [
            "item_type",
            "name",
            "sku",
            "category",
            "labels",
            "allergens",
            "short_description",
            "description",
            "unit",
            "sale_price",
            "purchase_price",
            "vat_rate",
            "minimum_stock",
            "is_stock_tracked",
            "show_image",
            "use_default_image_when_missing",
            "is_featured",
            "status",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "short_description": forms.TextInput(),
            "labels": forms.CheckboxSelectMultiple(),
            "allergens": forms.CheckboxSelectMultiple(),
        }
        help_texts = {
            "item_type": "Bepaalt hoe het item zich gedraagt. Gerechten en dranken kunnen een recept hebben. Ingrediënten worden gebruikt in recepten.",
            "name": "De naam die medewerkers en bezoekers zien.",
            "sku": "Optioneel intern artikelnummer of leverancierscode.",
            "category": "Categorie bepaalt waar het item in lijsten en filters staat.",
            "labels": "Labels maken filteren makkelijk. Bijvoorbeeld Populair, Vegetarisch, Pittig of Premium.",
            "allergens": "Kies allergenen die direct in dit item zitten. Bij gerechten worden allergenen van ingrediënten ook getoond.",
            "short_description": "Korte tekst voor kaarten en overzichten.",
            "description": "Langere tekst voor de detailpagina. Hier kun je sfeer, ingrediënten of uitleg kwijt.",
            "unit": "De vaste eenheid voor voorraad. Bijvoorbeeld stuk, gram, kilogram, liter of milliliter.",
            "sale_price": "Verkoopprijs voor klanten.",
            "purchase_price": "Inkoopprijs per vaste eenheid. Handig voor marge later.",
            "vat_rate": "Gebruik meestal 9 procent voor eten en non-alcoholisch, 21 procent voor alcohol. Controleer dit zelf.",
            "minimum_stock": "Onder deze waarde wordt lage voorraad getoond.",
            "is_stock_tracked": "Zet dit aan als je voorraad van dit item wilt bijhouden.",
            "show_image": "Zet dit uit als je geen media wilt tonen op publieke pagina’s.",
            "use_default_image_when_missing": "Gebruik de standaardafbeelding als er geen eigen media is.",
            "is_featured": "Toon dit item als uitgelicht op plekken zoals de homepagina.",
            "status": "Alleen actieve items zijn publiek zichtbaar.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["category"].queryset = Category.objects.filter(is_active=True).order_by("sort_order", "name")
        self.fields["labels"].queryset = Label.objects.order_by("name")
        self.fields["allergens"].queryset = Allergen.objects.filter(is_active=True).order_by("name")
        self.fields["unit"].queryset = Unit.objects.filter(is_active=True).order_by("unit_type", "name")

        self.fields["item_type"].label = "Type"
        self.fields["name"].label = "Naam"
        self.fields["sku"].label = "Artikelcode"
        self.fields["category"].label = "Categorie"
        self.fields["labels"].label = "Labels"
        self.fields["allergens"].label = "Allergenen"
        self.fields["short_description"].label = "Korte omschrijving"
        self.fields["description"].label = "Uitgebreide omschrijving"
        self.fields["unit"].label = "Vaste eenheid"
        self.fields["sale_price"].label = "Verkoopprijs"
        self.fields["purchase_price"].label = "Inkoopprijs per eenheid"
        self.fields["vat_rate"].label = "Btw percentage"
        self.fields["minimum_stock"].label = "Minimumvoorraad"
        self.fields["is_stock_tracked"].label = "Voorraad bijhouden"
        self.fields["show_image"].label = "Media tonen"
        self.fields["use_default_image_when_missing"].label = "Standaardafbeelding gebruiken als er geen media is"
        self.fields["is_featured"].label = "Uitgelicht tonen"
        self.fields["status"].label = "Status"

        media_choices = []
        if self.instance and self.instance.pk:
            media_files = self.instance.media_files.filter(is_public=True).order_by("sort_order", "uploaded_at", "id")
            media_choices = [
                (str(media.id), media.caption or media.alt_text or media.image.name)
                for media in media_files
            ]

            primary_media = media_files.filter(is_primary=True).first()
            if primary_media:
                self.fields["primary_media_id"].initial = str(primary_media.id)
            elif media_files.count() == 1:
                self.fields["primary_media_id"].initial = str(media_files.first().id)

        self.fields["primary_media_id"].choices = media_choices

        self.fields["labels"].required = False
        self.fields["allergens"].required = False
        self.fields["sku"].required = False
        self.fields["short_description"].required = False
        self.fields["description"].required = False
        self.fields["sale_price"].required = False
        self.fields["purchase_price"].required = False
        self.fields["minimum_stock"].required = False

    def clean_media_files(self):
        files = self.cleaned_data.get("media_files", [])

        for uploaded_file in files:
            suffix = Path(uploaded_file.name).suffix.lower()

            if suffix not in ALLOWED_MEDIA_EXTENSIONS:
                raise forms.ValidationError(
                    f"{uploaded_file.name} heeft een niet toegestaan bestandstype."
                )

            if uploaded_file.size > 25 * 1024 * 1024:
                raise forms.ValidationError(
                    f"{uploaded_file.name} is groter dan 25 MB."
                )

        return files

    def clean(self):
        cleaned_data = super().clean()

        is_stock_tracked = cleaned_data.get("is_stock_tracked")
        unit = cleaned_data.get("unit")

        if is_stock_tracked and not unit:
            raise forms.ValidationError("Kies een vaste eenheid als je voorraad wilt bijhouden.")

        return cleaned_data

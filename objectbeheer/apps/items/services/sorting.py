ITEM_TYPE_ORDER = {
    "menu_item": 10,
    "drink": 20,
    "product": 30,
    "ingredient": 40,
    "asset": 50,
    "service": 60,
    "storage_unit": 70,
    "property": 80,
}


CATEGORY_ORDER = {
    "Burgers": 10,
    "Friet": 20,
    "Loaded Fries": 25,
    "Snacks": 30,
    "Broodjes": 35,
    "Sauzen": 40,
    "Gerechten": 45,
    "Cocktails": 50,
    "Mocktails": 55,
    "Frisdrank": 60,
    "Warme dranken": 65,
    "Bier en wijn": 70,
    "Milkshakes": 75,
    "Desserts": 80,
    "Ingrediënten": 100,
    "Vlees en vis": 110,
    "Brood en deeg": 120,
    "Groente en fruit": 130,
    "Zuivel": 140,
    "Sauzen en toppings": 150,
    "Kruiden en smaakmakers": 160,
    "Dranken voorraad": 170,
    "Verpakking": 180,
}


def horeca_sort_key(row):
    item = row["item"] if isinstance(row, dict) else row

    return (
        ITEM_TYPE_ORDER.get(item.item_type, 999),
        CATEGORY_ORDER.get(item.category.name if item.category else "", 999),
        item.name.lower(),
    )

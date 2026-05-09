from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.items.models import Allergen


ALLERGENS = [
    ("Gluten", "Komt voor in tarwe, brood, wraps, paneermeel en veel snacks."),
    ("Melk", "Zuivel, kaas, room, melk en boter."),
    ("Ei", "Ei, mayonaise, schuimlagen en sommige sauzen."),
    ("Noten", "Boomnoten zoals amandel, hazelnoot en walnoot."),
    ("Pinda", "Pinda en pindasauzen zoals satésaus."),
    ("Soja", "Soja en producten op basis van soja."),
    ("Vis", "Vis en visproducten."),
    ("Schaaldieren", "Garnalen, krab en vergelijkbare producten."),
    ("Selderij", "Selderij en selderijhoudende kruidenmixen."),
    ("Mosterd", "Mosterd en mosterdhoudende sauzen."),
    ("Sesam", "Sesamzaad en sesamolie."),
    ("Sulfiet", "Kan voorkomen in wijn, gedroogd fruit en sommige sauzen."),
    ("Lupine", "Lupine en producten op basis van lupine."),
    ("Weekdieren", "Mosselen, oesters, inktvis en vergelijkbare producten."),
]


class Command(BaseCommand):
    help = "Voegt standaard allergenen toe."

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for name, description in ALLERGENS:
            allergen, was_created = Allergen.objects.update_or_create(
                slug=slugify(name),
                defaults={
                    "name": name,
                    "description": description,
                    "is_active": True,
                },
            )

            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Allergenen klaar. Nieuw: {created}. Bijgewerkt: {updated}."))

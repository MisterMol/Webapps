from django.core.management.base import BaseCommand

from apps.items.models import Item


class Command(BaseCommand):
    help = "Toont items zonder publieke media."

    def handle(self, *args, **options):
        items = (
            Item.objects
            .filter(status="active", item_type__in=["menu_item", "drink", "product"])
            .prefetch_related("media_files")
            .order_by("item_type", "name")
        )

        missing = []

        for item in items:
            has_public_media = item.media_files.filter(is_public=True).exists()

            if not has_public_media:
                missing.append(item)

        if not missing:
            self.stdout.write(self.style.SUCCESS("Alle actieve gerechten, dranken en producten hebben media."))
            return

        self.stdout.write(self.style.WARNING(f"Items zonder media: {len(missing)}"))

        for item in missing:
            self.stdout.write(f"- {item.name} ({item.get_item_type_display()}) verwacht bestand: {item.slug}.jpg")

from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.items.models import Item, ItemImage


SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".avif",
    ".gif",
    ".mp4",
    ".webm",
    ".mov",
}


def detect_media_kind(path):
    suffix = path.suffix.lower()

    if suffix in [".jpg", ".jpeg", ".png", ".webp", ".avif", ".svg"]:
        return "image"

    if suffix == ".gif":
        return "gif"

    if suffix in [".mp4", ".webm", ".mov"]:
        return "video"

    return "other"


class Command(BaseCommand):
    help = "Importeert itemfoto's uit media/import/item_photos en koppelt ze aan items op basis van slug."

    def handle(self, *args, **options):
        import_dir = Path("media/import/item_photos")

        if not import_dir.exists():
            self.stdout.write(self.style.ERROR("Map media/import/item_photos bestaat niet."))
            return

        imported_count = 0
        skipped_count = 0

        for file_path in sorted(import_dir.iterdir()):
            if not file_path.is_file():
                continue

            if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f"Overgeslagen, niet ondersteund: {file_path.name}"))
                continue

            item_slug = slugify(file_path.stem)
            item = Item.objects.filter(slug=item_slug).first()

            if not item:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f"Geen item gevonden voor bestand: {file_path.name}"))
                continue

            already_exists = ItemImage.objects.filter(
                item=item,
                image__icontains=file_path.name,
            ).exists()

            if already_exists:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f"Bestaat al: {file_path.name}"))
                continue

            has_primary = ItemImage.objects.filter(item=item, is_primary=True).exists()

            with file_path.open("rb") as photo_file:
                media = ItemImage.objects.create(
                    item=item,
                    media_kind=detect_media_kind(file_path),
                    alt_text=item.name,
                    caption=item.name,
                    sort_order=0,
                    is_primary=not has_primary,
                    is_public=True,
                )
                media.image.save(file_path.name, File(photo_file), save=True)

            imported_count += 1
            self.stdout.write(self.style.SUCCESS(f"Geïmporteerd: {file_path.name} gekoppeld aan {item.name}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Klaar. Geïmporteerd: {imported_count}. Overgeslagen: {skipped_count}."
            )
        )

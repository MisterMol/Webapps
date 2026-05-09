from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image, ImageOps

from apps.items.models import ItemImage


THUMB_WIDTH = 700
THUMB_HEIGHT = 525


def crop_center_cover(image, target_width, target_height):
    """
    Snijdt een afbeelding bij zodat hij het doelvlak volledig vult.

    Dit werkt zoals CSS object-fit: cover.
    Dus geen zwarte randen, maar professioneel beeldvullend.
    """
    source_width, source_height = image.size
    target_ratio = target_width / target_height
    source_ratio = source_width / source_height

    if source_ratio > target_ratio:
        new_width = int(source_height * target_ratio)
        left = (source_width - new_width) // 2
        box = (left, 0, left + new_width, source_height)
    else:
        new_height = int(source_width / target_ratio)
        top = (source_height - new_height) // 2
        box = (0, top, source_width, top + new_height)

    image = image.crop(box)
    return image.resize((target_width, target_height), Image.Resampling.LANCZOS)


class Command(BaseCommand):
    help = "Maakt snelle webp thumbnails voor itemmedia met professionele cover crop."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Maak thumbnails opnieuw, ook als ze al bestaan.",
        )

    def handle(self, *args, **options):
        force = options["force"]

        media_root = Path(settings.MEDIA_ROOT)
        thumb_dir = media_root / "items" / "thumbs"
        thumb_dir.mkdir(parents=True, exist_ok=True)

        created = 0
        skipped = 0
        failed = 0

        media_files = (
            ItemImage.objects
            .filter(is_public=True, media_kind__in=["image", "gif"])
            .select_related("item")
            .order_by("item__name", "id")
        )

        for media in media_files:
            if not media.image:
                skipped += 1
                continue

            source_path = Path(media.image.path)

            if not source_path.exists():
                self.stdout.write(self.style.WARNING(f"Bestand bestaat niet: {source_path}"))
                failed += 1
                continue

            thumb_name = f"{media.item.slug}-{media.id}.webp"
            thumb_path = thumb_dir / thumb_name

            if thumb_path.exists() and not force:
                skipped += 1
                continue

            try:
                with Image.open(source_path) as image:
                    image = ImageOps.exif_transpose(image)

                    if getattr(image, "is_animated", False):
                        image.seek(0)

                    image = image.convert("RGB")
                    thumbnail = crop_center_cover(image, THUMB_WIDTH, THUMB_HEIGHT)

                    thumbnail.save(
                        thumb_path,
                        "WEBP",
                        quality=82,
                        method=6,
                    )

                created += 1
                self.stdout.write(self.style.SUCCESS(f"Thumbnail gemaakt: {thumb_path}"))

            except Exception as error:
                failed += 1
                self.stdout.write(self.style.ERROR(f"Mislukt voor {source_path}: {error}"))

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Klaar. Gemaakt: {created}. Overgeslagen: {skipped}. Mislukt: {failed}."
            )
        )

from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.inventory.models import StockMovement, calculate_stock, item_is_available
from apps.inventory.services import book_stock
from apps.recipes.models import RecipeIngredient, get_recipe_availability

from .forms import ItemCreateForm, ItemUpdateForm
from .models import Category, Item, ItemImage, Label
from .services.sorting import horeca_sort_key


def detect_media_kind(filename):
    suffix = Path(filename).suffix.lower()

    if suffix in [".jpg", ".jpeg", ".png", ".webp", ".avif", ".svg"]:
        return "image"

    if suffix == ".gif":
        return "gif"

    if suffix in [".mp4", ".webm", ".mov"]:
        return "video"

    return "other"



def paginate_rows(rows, request, per_page=36):
    paginator = Paginator(rows, per_page)
    page_number = request.GET.get("page") or 1
    return paginator.get_page(page_number)


def filter_items(queryset, request, public_only=False):
    search_query = request.GET.get("q", "").strip()
    item_type = request.GET.get("type", "").strip()
    category_slug = request.GET.get("categorie", "").strip()
    label_slug = request.GET.get("label", "").strip()
    availability = request.GET.get("beschikbaarheid", "").strip()

    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query)
            | Q(short_description__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(sku__icontains=search_query)
        )

    if item_type:
        queryset = queryset.filter(item_type=item_type)

    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)

    if label_slug:
        queryset = queryset.filter(labels__slug=label_slug)

    queryset = queryset.distinct()

    rows = []

    for item in queryset:
        stock = calculate_stock(item) if item.is_stock_tracked else None
        available = item_is_available(item)

        if public_only and not available:
            continue

        if availability == "available" and not available:
            continue

        if availability == "unavailable" and available:
            continue

        recipe_availability = None

        if item.item_type in ["menu_item", "drink"]:
            recipe_availability = get_recipe_availability(item)

        rows.append(
            {
                "item": item,
                "stock": stock,
                "available": available,
                "recipe_availability": recipe_availability,
            }
        )

    return sorted(rows, key=horeca_sort_key)


def public_item_list(request):
    base_queryset = (
        Item.objects
        .filter(status="active", item_type__in=["menu_item", "drink", "product"])
        .select_related("category", "unit")
        .prefetch_related("media_files", "labels", "stock_movements")
    )

    rows = filter_items(base_queryset, request, public_only=True)
    page_obj = paginate_rows(rows, request, per_page=24)

    return render(
        request,
        "items/public_item_list.html",
        {
            "rows": page_obj.object_list,
            "page_obj": page_obj,
            "categories": Category.objects.filter(is_active=True).order_by("sort_order", "name"),
            "labels": Label.objects.order_by("name"),
            "selected_type": request.GET.get("type", ""),
            "selected_category": request.GET.get("categorie", ""),
            "selected_label": request.GET.get("label", ""),
            "selected_availability": request.GET.get("beschikbaarheid", ""),
            "search_query": request.GET.get("q", ""),
        },
    )


def public_item_detail(request, slug):
    item = get_object_or_404(
        Item.objects.filter(status="active", item_type__in=["menu_item", "drink", "product"])
        .select_related("category", "unit")
        .prefetch_related("media_files", "labels", "stock_movements"),
        slug=slug,
    )

    if not item_is_available(item):
        return render(
            request,
            "items/not_available.html",
            {
                "item": item,
            },
            status=404,
        )

    recipe_availability = None
    recipe_lines = []
    used_in_recipe_lines = []
    stock = calculate_stock(item) if item.is_stock_tracked else None

    if item.item_type in ["menu_item", "drink"]:
        recipe_availability = get_recipe_availability(item)

        if recipe_availability["has_recipe"]:
            recipe_lines = (
                item.recipe.ingredients
                .select_related("ingredient", "ingredient__unit", "ingredient__category")
                .order_by("is_optional", "ingredient__name")
            )

    if item.item_type in ["ingredient", "product"]:
        used_in_recipe_lines = (
            RecipeIngredient.objects
            .filter(ingredient=item)
            .select_related("recipe", "recipe__output_item", "recipe__output_item__category")
            .order_by("recipe__output_item__name")
        )

    recent_movements = (
        StockMovement.objects
        .filter(item=item)
        .select_related("location", "unit", "created_by")
        .order_by("-created_at")[:10]
    )

    return render(
        request,
        "items/public_item_detail.html",
        {
            "item": item,
            "recipe_availability": recipe_availability,
            "recipe_lines": recipe_lines,
            "used_in_recipe_lines": used_in_recipe_lines,
            "stock": stock,
            "recent_movements": recent_movements,
        },
    )


@login_required
@permission_required("items.view_item", raise_exception=True)
def dashboard_item_list(request):
    base_queryset = (
        Item.objects
        .select_related("category", "unit")
        .prefetch_related("media_files", "labels", "stock_movements")
    )

    rows = filter_items(base_queryset, request, public_only=False)
    page_obj = paginate_rows(rows, request, per_page=36)

    counts = {
        "all": Item.objects.count(),
        "products": Item.objects.filter(item_type="product").count(),
        "menu_items": Item.objects.filter(item_type="menu_item").count(),
        "ingredients": Item.objects.filter(item_type="ingredient").count(),
        "drinks": Item.objects.filter(item_type="drink").count(),
    }

    return render(
        request,
        "items/dashboard_item_list.html",
        {
            "rows": page_obj.object_list,
            "page_obj": page_obj,
            "counts": counts,
            "categories": Category.objects.filter(is_active=True).order_by("sort_order", "name"),
            "labels": Label.objects.order_by("name"),
            "selected_type": request.GET.get("type", ""),
            "selected_category": request.GET.get("categorie", ""),
            "selected_label": request.GET.get("label", ""),
            "selected_availability": request.GET.get("beschikbaarheid", ""),
            "search_query": request.GET.get("q", ""),
        },
    )


@login_required
@permission_required("items.add_item", raise_exception=True)
def item_create(request, item_type=None):
    if request.method == "POST":
        form = ItemCreateForm(request.POST, request.FILES, item_type=item_type)

        if form.is_valid():
            item = form.save()

            primary_media_id = form.cleaned_data.get("primary_media_id")
            if primary_media_id:
                item.media_files.update(is_primary=False)
                item.media_files.filter(id=primary_media_id).update(is_primary=True)

            uploaded_files = form.cleaned_data.get("media_files", [])

            for index, uploaded_file in enumerate(uploaded_files):
                ItemImage.objects.create(
                    item=item,
                    image=uploaded_file,
                    media_kind=detect_media_kind(uploaded_file.name),
                    alt_text=item.name,
                    sort_order=index,
                    is_primary=index == 0,
                    is_public=True,
                )

            initial_stock_quantity = form.cleaned_data.get("initial_stock_quantity")

            if initial_stock_quantity:
                book_stock(
                    item=item,
                    movement_type="purchase",
                    quantity=initial_stock_quantity,
                    user=request.user,
                    location=form.cleaned_data["initial_stock_location"],
                    unit=form.cleaned_data.get("initial_stock_unit") or item.unit,
                    reason_code="purchase",
                    reason="Directe inkoop bij aanmaken item",
                    note=form.cleaned_data.get("initial_stock_note", ""),
                )

            messages.success(request, f"{item.name} is aangemaakt.")
            return redirect("items:dashboard_list")
    else:
        form = ItemCreateForm(
            item_type=item_type,
            initial={
                "item_type": item_type or "product",
                "status": "active",
                "show_image": True,
                "use_default_image_when_missing": True,
            },
        )

    title_map = {
        "product": "Nieuw product",
        "drink": "Nieuwe drank",
        "ingredient": "Nieuw ingrediënt",
        "menu_item": "Nieuw gerecht",
    }

    return render(
        request,
        "items/item_form.html",
        {
            "form": form,
            "title": title_map.get(item_type, "Nieuw product of ingrediënt"),
            "item_type": item_type,
        },
    )


@login_required
@permission_required("items.change_item", raise_exception=True)
def item_update(request, item_id):
    item = get_object_or_404(
        Item.objects
        .select_related("category", "unit")
        .prefetch_related("labels", "media_files"),
        id=item_id,
    )

    if request.method == "POST":
        form = ItemUpdateForm(request.POST, request.FILES, instance=item)

        if form.is_valid():
            item = form.save()

            primary_media_id = form.cleaned_data.get("primary_media_id")
            if primary_media_id:
                item.media_files.update(is_primary=False)
                item.media_files.filter(id=primary_media_id).update(is_primary=True)

            uploaded_files = form.cleaned_data.get("media_files", [])

            has_primary = item.media_files.filter(is_primary=True).exists()

            for index, uploaded_file in enumerate(uploaded_files):
                ItemImage.objects.create(
                    item=item,
                    image=uploaded_file,
                    media_kind=detect_media_kind(uploaded_file.name),
                    alt_text=item.name,
                    caption=item.name,
                    sort_order=item.media_files.count() + index,
                    is_primary=not has_primary and index == 0,
                    is_public=True,
                )

            messages.success(request, f"{item.name} is aangepast.")
            return redirect("items:dashboard_list")
    else:
        form = ItemUpdateForm(instance=item)

    stock = calculate_stock(item) if item.is_stock_tracked else None

    used_in_recipe_lines = (
        RecipeIngredient.objects
        .filter(ingredient=item)
        .select_related("recipe", "recipe__output_item", "recipe__output_item__category")
        .order_by("recipe__output_item__name")
    )

    recipe_availability = None

    if item.item_type in ["menu_item", "drink"]:
        recipe_availability = get_recipe_availability(item)

    recent_movements = (
        StockMovement.objects
        .filter(item=item)
        .select_related("location", "unit", "created_by")
        .order_by("-created_at")[:8]
    )

    return render(
        request,
        "items/item_update.html",
        {
            "form": form,
            "item": item,
            "stock": stock,
            "used_in_recipe_lines": used_in_recipe_lines,
            "recipe_availability": recipe_availability,
            "recent_movements": recent_movements,
        },
    )

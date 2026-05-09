from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.inventory.models import calculate_stock
from apps.items.models import Item
from apps.items.services.sorting import horeca_sort_key

from .forms import RecipeForm, RecipeIngredientForm
from .models import Recipe, RecipeIngredient, get_recipe_availability


@login_required
def recipe_list(request):
    recipes = Recipe.objects.select_related("output_item").prefetch_related("ingredients")
    return render(request, "recipes/list.html", {"recipes": recipes})


@login_required
@permission_required("recipes.view_recipe", raise_exception=True)
def recipe_availability_overview(request):
    recipe_items = (
        Item.objects
        .filter(status="active", item_type__in=["menu_item", "drink"])
        .select_related("category", "unit")
        .prefetch_related("media_files", "labels")
        .order_by("category__name", "name")
    )

    rows = []

    for item in recipe_items:
        availability = get_recipe_availability(item)
        rows.append(
            {
                "item": item,
                "availability": availability,
            }
        )

    rows = sorted(rows, key=horeca_sort_key)

    return render(
        request,
        "recipes/availability.html",
        {
            "rows": rows,
        },
    )


@login_required
@permission_required("recipes.change_recipe", raise_exception=True)
def recipe_manage(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    recipe, _ = Recipe.objects.get_or_create(output_item=item, defaults={"servings": 1})

    if request.method == "POST":
        recipe_form = RecipeForm(request.POST, instance=recipe)
        ingredient_form = RecipeIngredientForm(request.POST, recipe=recipe)

        if "save_recipe" in request.POST and recipe_form.is_valid():
            recipe_form.save()
            messages.success(request, "Receptinstellingen zijn opgeslagen.")
            return redirect("recipes:manage", item_id=item.id)

        if "add_ingredient" in request.POST and ingredient_form.is_valid():
            line = ingredient_form.save(commit=False)
            line.recipe = recipe
            line.save()
            messages.success(request, f"{line.ingredient.name} is toegevoegd aan het recept.")
            return redirect("recipes:manage", item_id=item.id)
    else:
        recipe_form = RecipeForm(instance=recipe)
        ingredient_form = RecipeIngredientForm(recipe=recipe)

    availability = get_recipe_availability(item)

    lines = (
        recipe.ingredients
        .select_related("ingredient", "ingredient__unit", "ingredient__category")
        .order_by("is_optional", "ingredient__name")
    )

    line_rows = []

    for line in lines:
        line_rows.append(
            {
                "line": line,
                "stock": calculate_stock(line.ingredient),
            }
        )

    return render(
        request,
        "recipes/manage.html",
        {
            "item": item,
            "recipe": recipe,
            "recipe_form": recipe_form,
            "ingredient_form": ingredient_form,
            "line_rows": line_rows,
            "availability": availability,
        },
    )


@login_required
@permission_required("recipes.change_recipe", raise_exception=True)
def recipe_ingredient_update(request, line_id):
    line = get_object_or_404(
        RecipeIngredient.objects.select_related(
            "recipe",
            "recipe__output_item",
            "ingredient",
        ),
        id=line_id,
    )

    if request.method == "POST":
        form = RecipeIngredientForm(request.POST, instance=line, recipe=line.recipe)

        if form.is_valid():
            form.save()
            messages.success(request, f"{line.ingredient.name} is aangepast.")
            return redirect("recipes:manage", item_id=line.recipe.output_item_id)
    else:
        form = RecipeIngredientForm(instance=line, recipe=line.recipe)

    return render(
        request,
        "recipes/ingredient_form.html",
        {
            "form": form,
            "line": line,
            "recipe": line.recipe,
            "item": line.recipe.output_item,
            "title": f"Ingrediënt aanpassen: {line.ingredient.name}",
        },
    )


@login_required
@permission_required("recipes.change_recipe", raise_exception=True)
def recipe_ingredient_delete(request, line_id):
    line = get_object_or_404(
        RecipeIngredient.objects.select_related("recipe", "ingredient"),
        id=line_id,
    )
    item_id = line.recipe.output_item_id
    ingredient_name = line.ingredient.name

    if request.method == "POST":
        line.delete()
        messages.success(request, f"{ingredient_name} is verwijderd uit het recept.")

    return redirect("recipes:manage", item_id=item_id)

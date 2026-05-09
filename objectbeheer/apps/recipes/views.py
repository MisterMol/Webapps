from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Recipe


@login_required
def recipe_list(request):
    recipes = Recipe.objects.select_related("output_item").prefetch_related("ingredients")
    return render(request, "recipes/list.html", {"recipes": recipes})

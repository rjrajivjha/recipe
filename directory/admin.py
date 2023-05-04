from django.contrib import admin
from .models import Recipe, Cuisine, RecipeIngredients, Ingredients, MealTypes, MeatTypes


# Register your models here.


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(Cuisine)
class CuisineAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(RecipeIngredients)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "ingredient")


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(MealTypes)
class MealTypesAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(MeatTypes)
class MeatTypesAdmin(admin.ModelAdmin):
    list_display = ("id", "name")

from django.contrib import admin
from .models import Recipe, Cuisine, RecipeIngredients, Ingredient, MealTypes, MeatTypes


# Register your models here.


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(Cuisine)
class CuisineAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(RecipeIngredients)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "ingredient", "comments", "unit_value", "unit_data_type", "unit_type", "variation")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(MealTypes)
class MealTypesAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(MeatTypes)
class MeatTypesAdmin(admin.ModelAdmin):
    list_display = ("id", "name")

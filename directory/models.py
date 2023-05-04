from django.db import models
from .constants import RECIPE_TYPE, MEAT_CATEGORY, UNIT_DATA_TYPE, UNIT_TYPE


class BaseModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Cuisine(BaseModel):
    name = models.CharField(max_length=128, null=False, blank=False, unique=True)

    # TODO:
    # before saving convert all to either CAPS or small letter by signal

    def __str__(self):
        return f"{self.name}"


class MeatTypes(BaseModel):
    name = models.CharField(max_length=128, null=False, blank=False, unique=True)

    def __str__(self):
        return f"{self.name}"


class MealTypes(BaseModel):
    name = models.CharField(max_length=128, null=False, blank=False, unique=True)

    def __str__(self):
        return f"{self.name}"


class Ingredient(BaseModel):
    name = models.CharField(max_length=128, null=False, blank=False, unique=True)

    def __str__(self):
        return f"{self.name}"


class Recipe(BaseModel):
    pdf_number = models.CharField(max_length=128, null=True, blank=True)
    name = models.CharField(max_length=128, null=False, blank=False, unique=True)
    alternate_name = models.CharField(max_length=128, null=True, blank=True)
    recipe_type = models.CharField(max_length=128, choices=RECIPE_TYPE, default=None, null=True)
    description = models.TextField(blank=True, null=True, default=None)
    meat_type = models.ForeignKey(MeatTypes, on_delete=models.CASCADE, null=True)
    meat_category = models.CharField(max_length=128, choices=MEAT_CATEGORY, default=None, null=True)
    cuisine = models.ForeignKey(Cuisine, on_delete=models.CASCADE, null=True)
    serving_quantity = models.CharField(max_length=128, null=True, blank=True)
    serving_quantity_unit = models.CharField(max_length=128, null=True, blank=True)
    min_serve = models.CharField(max_length=128, null=True, blank=True)
    max_serve = models.CharField(max_length=128, null=True, blank=True)
    meal_type = models.ForeignKey(MealTypes, on_delete=models.CASCADE, null=True)
    cookware = models.TextField(blank=True, null=True, default=None)
    calories = models.CharField(max_length=128, null=True, blank=True)
    cooking = models.TextField(blank=True, null=True, default=None)
    pre_cooking = models.TextField(blank=True, null=True, default=None)
    cook_tip = models.TextField(blank=True, null=True, default=None)
    serve_tip = models.TextField(blank=True, null=True, default=None)
    others_tip = models.TextField(blank=True, null=True, default=None)

    cook_time = models.CharField(max_length=128, null=True, blank=True)
    prep_time = models.CharField(max_length=128, null=True, blank=True)
    soak_time = models.CharField(max_length=128, null=True, blank=True)
    marinate_time = models.CharField(max_length=128, null=True, blank=True)
    total_time = models.CharField(max_length=128, null=True, blank=True)

    energy = models.CharField(max_length=128, null=True, blank=True)
    k_cal = models.CharField(max_length=128, null=True, blank=True)
    cal = models.CharField(max_length=128, null=True, blank=True)
    carbohydrate = models.CharField(max_length=128, null=True, blank=True)
    sugars = models.CharField(max_length=128, null=True, blank=True)
    fat = models.CharField(max_length=128, null=True, blank=True)
    saturated_fat = models.CharField(max_length=128, null=True, blank=True)
    cholesterol = models.CharField(max_length=128, null=True, blank=True)
    calcium = models.CharField(max_length=128, null=True, blank=True)
    fibre = models.CharField(max_length=128, null=True, blank=True)
    sodium = models.CharField(max_length=128, null=True, blank=True)
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredients')

    def __str__(self):
        return f"{self.name}"


class RecipeIngredients(BaseModel):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, unique=False, blank=False, null=False, default=None)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, unique=False, blank=False, null=False,
                                   default=None)
    alternate = models.CharField(max_length=128, blank=True, null=True, default=None)
    comments = models.TextField(blank=True, null=True, default=None)
    unit_value = models.CharField(max_length=128, default=None, null=True)
    unit_data_type = models.CharField(max_length=128, choices=UNIT_DATA_TYPE, default=None, null=True)
    unit_type = models.CharField(max_length=128, choices=UNIT_TYPE, default=None, null=True)
    variation = models.TextField(blank=True, null=True, default=None)

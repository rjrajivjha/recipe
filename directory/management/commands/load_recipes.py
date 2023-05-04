#!/usr/bin/env python3.7
import logging
import numpy as np
import pandas as pd
import os
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

from ...constants import UNIT_TYPE, NUMBER, STRING
from ...models import Recipe, Cuisine, RecipeIngredients, MeatTypes, MealTypes, Ingredients
from .utils import parse_reader, send_email, sanitized


class Command(BaseCommand):
    help = """
    
        This script will dump data from the file 'recipe.xsl' into the DB. 
        
        Below is the input file format :
         
        Sl. No, pdf Number, Recipe Name, .... , Sodium
    
        management command usage:
        python manage.py load_recipes --input /path_to/file.xsl 
        python manage.py load_recipes -i data/test_1.xlsx
        """

    def add_arguments(self, parser):
        parser.add_argument(
            "-i",
            "--input-file",
            dest="input-file",
            help="CSV-file containing Recipe data",
        )
        parser.add_argument(
            "-d",
            "--dry-run",
            action='store_true',
            dest='dry_run',
            default=False,
            help='Don\'t actually create the Recipe records',
        )
        parser.add_argument(
            "-o",
            "--output",
            default=False,
            action="store",
            dest="output",
            help="log file path to writing the data.",
        )
        parser.add_argument(
            "-r",
            "--recipient",
            default="fork.rajiv@gmail.com",
            action="store",
            dest="output",
            help="Recipient for the update email",
        )

    def handle(self, *args, **options):
        if options.get('output'):
            output_file = options.get('output')
        else:
            output_file = "data/output.csv"
        if options.get('input-file'):
            input_file = options.get('input-file')
            helper = RecipeDump(options)
            helper.process(input_file, output_file)
        else:
            self.stdout.write(
                "Please provide input file and output log file. \n"
                "python manage.py load_recipes --input "
                "/path/input_file.csv --output /path/output_file.csv"
            )


class RecipeDump(object):
    def __init__(self, options, **kwargs):
        self.recipient = "fork.rajiv@gmail.com"
        # self.recipient = options['recipient']
        self.dry_run = options['dry_run']
        self.logger = logging.getLogger('management.load_recipes')

    def save_recipe_ingredient(self, recipe, ingredient, alternate, record):
        recipe_ingredients = RecipeIngredients()
        for unit_value in UNIT_TYPE:
            if not pd.isna(record[unit_value[1].lower()]):
                recipe_ingredients.unit_value = record[unit_value[1].lower()]
                recipe_ingredients.unit_type = unit_value[1]
                recipe_ingredients.unit_data_type = NUMBER if type(record[unit_value[1].lower()]) is not str else STRING

        recipe_ingredients.recipe = recipe
        recipe_ingredients.ingredient = ingredient
        recipe_ingredients.alternate = alternate
        recipe_ingredients.comments = record["comments"]
        recipe_ingredients.variation = record["variation / alternate"]
        recipe_ingredients.save()

    def process(self, input_file, output_file):
        objects = []
        recipe = Recipe()
        with open(output_file, 'w') as out_file:
            records = parse_reader(input_file)
            next_recipe_flag = True
            for idx, record in enumerate(records):
                if (not pd.isna(record["sl. no"])) or (not pd.isna(record["recipe name"])):
                    recipe = Recipe()
                    try:
                        cuisine = Cuisine.objects.get(name=sanitized(record["cuisine"]))
                        meat_type = MeatTypes.objects.get(name=sanitized(record["meat type"]))
                        meal_type = MealTypes.objects.get(name=sanitized(record["meal type"]))
                        ingredient = Ingredients.objects.get(name=sanitized(record["actual"]))
                        alternate_ing = Ingredients.objects.get(name=sanitized(record["alternate"]))
                    except Exception as e:
                        out_file.write(f"\n Either Cuisine, meat type or meal type data is not loaded."
                                       f"at line {idx + 1}: {e}")
                        self.logger.warning(f"\n Either Cuisine, meat type or meal type data is not loaded."
                                            f"at line {idx + 1}: {e}")
                        next_recipe_flag = True
                        continue
                    recipe.cuisine = cuisine
                    recipe.meat_type = meat_type
                    recipe.meal_type = meal_type
                    recipe.pdf_number = record["pdf number"]
                    recipe.name = record["recipe name"]
                    recipe.alternate_name = record["alternate name"]
                    recipe.recipe_type = record["recipe type"]
                    recipe.description = record["description"]
                    recipe.meat_category = record["meat classification"]
                    recipe.serving_quantity = record["serving quantity"]
                    recipe.cookware = record["cookware"]
                    recipe.calories = record["calories per serving"]

                    try:
                        recipe.min_serve, recipe.max_serve = record["serve"].split("-")
                    except Exception as e:
                        recipe.min_serve = recipe.max_serve = record["serve"]

                    recipe.cooking = record["cooking"]
                    recipe.pre_cooking = record["pre- cooking"]

                    recipe.cook_tip = record["cook tip"]
                    recipe.serve_tip = record["serve tip"]
                    recipe.others_tip = record["others"]

                    recipe.cook_time = record["cook time"]
                    recipe.prep_time = record["prep time"]
                    recipe.soak_time = record["soak time"]
                    recipe.marinate_time = record["marinate time"]
                    recipe.total_time = record["total"]

                    recipe.energy = record["energy"]
                    recipe.protein = record["protein"]
                    recipe.k_cal = record["kcal"]
                    recipe.cal = record["cal"]
                    recipe.carbohydrate = record["carbohydrate"]
                    recipe.sugars = record["sugars"]
                    recipe.fat = record["fat"]
                    recipe.saturated_fat = record["saturated fat"]
                    recipe.cholesterol = record["cholesterol"]
                    recipe.calcium = record["calcium"]
                    recipe.fibre = record["fibre"]
                    recipe.sodium = record["sodium"]
                    recipe.save()
                    next_recipe_flag = False

                    # recipe ingredient save
                    self.save_recipe_ingredient(recipe, ingredient, alternate_ing, record)

                else:
                    if next_recipe_flag:
                        continue
                    else:
                        try:
                            ingredient = Ingredients.objects.get(name=sanitized(record["actual"]))
                            alternate_ing = Ingredients.objects.get(name=sanitized(record["alternate"]))
                            self.save_recipe_ingredient(recipe, ingredient, alternate_ing, record)
                        except Exception as e:
                            out_file.write(f"\n Ingredient is not loaded."
                                           f"at line {idx + 1}: {e}")
                            self.logger.warning(f"\n Ingredient is not loaded."
                                                f"at line {idx + 1}: {e}")
                            next_recipe_flag = True
                            continue
                        # recipe ingredient save
        htmlgen = f'Hi, There is a update to your upload recipe report.'
        send_email("Load Recipe", htmlgen, output_file, self.recipient)
        os.remove(output_file)

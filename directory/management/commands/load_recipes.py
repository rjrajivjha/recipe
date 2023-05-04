#!/usr/bin/env python3.7
import logging
import numpy as np
import pandas as pd

from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist


from ...models import Recipe, Cuisine, RecipeIngredients, MeatTypes, MealTypes, Ingredients
from .utils import parse_reader


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
            '--delimiter',
            action='store',
            dest='delimiter',
            default="|",
            help='file delimiter (default "|") ',
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
        self.delimiter = options['delimiter']
        self.dry_run = options['dry_run']
        self.logger = logging.getLogger('management.load_recipes')

    def bulk_save(self, objects):
        with transaction.atomic():
            for obj in objects:
                obj.save()

    def process(self, input_file, output_file):
        objects = []

        with open(output_file, 'w') as out_file:
                records = parse_reader(input_file)
                for record in records:
                    if (not pd.isna(record["Sl. No"])) or (not pd.isna(record["Recipe Name"])):
                        # record started
                        # print(int(record["Sl. No"]), record["Recipe Name"].strip())
                        recipe = Recipe()
                        try:
                            cuisine = Cuisine.objects.get(name=record["Cuisine"])
                        except Cuisine.DoesNotExist:
                            cuisine = Cuisine()
                            cuisine.name = record["Cuisine"]

                        try:
                            meat_type = MeatTypes.objects.get(name=record["Meat Type"])
                        except MeatTypes.DoesNotExist:
                            meat_type = MeatTypes()
                            meat_type.name = record["Meat Type"]

                        try:
                            meal_type = MealTypes.objects.get(name=record["meal type"])
                        except MealTypes.DoesNotExist:
                            meal_type = MeatTypes()
                            meal_type.name = record["meal type"]

                        recipe.name = record["Recipe Name"]
                        recipe.alternate_name = record["Alternate Name"]
                        print(recipe, meal_type, meat_type, cuisine)
                        ingredients = Ingredients()
                    else:
                        ingredients = Ingredients()
                        recipe_ingredients = RecipeIngredients()

                    if self.dry_run:
                        # add recipe to objects
                        pass
                    else:
                        # add recipe to objects
                        # save objects
                        pass

                if not self.dry_run:
                    self.bulk_save(objects)

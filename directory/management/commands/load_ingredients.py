#!/usr/bin/env python3.7
import logging
import numpy as np
import pandas as pd
import os

from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

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

    def handle(self, *args, **options):
        if options.get('output'):
            output_file = options.get('output')
        else:
            output_file = "data/output_ingredients.csv"
        if options.get('input-file'):
            input_file = options.get('input-file')
            helper = IngredientDump(options)
            helper.process(input_file, output_file)
        else:
            self.stdout.write(
                "Please provide input file and output log file. \n"
                "python manage.py load_recipes --input "
                "/path/input_file.csv --output /path/output_file.csv"
            )



class IngredientDump(object):
    def __init__(self, options, **kwargs):
        self.recipient = "fork.rajiv@gmail.com"
        self.dry_run = options['dry_run']  # can be used for dry run option
        self.logger = logging.getLogger('management.load_ingredients')

    def process(self, input_file, output_file):
        objects = []

        with open(output_file, 'w') as out_file:
            records = parse_reader(input_file)
            for idx, record in enumerate(records):
                if not pd.isna(record["actual"]):
                    try:
                        ingredient = Ingredients.objects.get(name=sanitized(record["actual"]))
                    except Ingredients.DoesNotExist as e:
                        ingredient = Ingredients()
                        ingredient.name = sanitized(record["actual"])
                        ingredient.save()
                    except Exception as e:
                        out_file.write(f"\n Ingredient data is not loaded."
                                       f"at line {idx + 1}:  {record['actual']} . Error was:  {e}")
                        self.logger.warning(f"\n Ingredient data is not loaded."
                                       f"at line {idx + 1}:  {record['actual']} . Error was:  {e}")
                        continue
                    print(ingredient.name)

                if not pd.isna(record["alternate"]):
                    try:
                        alt_ingredient = Ingredients.objects.get(name=sanitized(record["alternate"]))
                    except Ingredients.DoesNotExist:
                        alt_ingredient = Ingredients()
                        alt_ingredient.name = sanitized(record["alternate"])
                        alt_ingredient.save()
                    except Exception as e:
                        out_file.write(f"\n alternate data is not loaded."
                                       f"at line {idx + 1}:  {record['alternate']} . Error was:  {e}")
                        self.logger.warning(f"\n alternate data is not loaded."
                                       f"at line {idx + 1}:  {record['alternate']} . Error was:  {e}")
                        continue

                if (not pd.isna(record["sl. no"])) or (not pd.isna(record["recipe name"])):

                    try:
                        cuisine = Cuisine.objects.get(name=sanitized(record["cuisine"]))
                    except Cuisine.DoesNotExist:
                        cuisine = Cuisine()
                        cuisine.name = sanitized(record["cuisine"])
                        cuisine.save()
                    except Exception as e:
                        out_file.write(f"\n Cuisine data is not loaded."
                                       f"at line {idx + 1}:  {record['cuisine']} . Error was:  {e}")
                        self.logger.warning(f"\n Cuisine data is not loaded."
                                       f"at line {idx + 1}:  {record['cuisine']} . Error was:  {e}")
                        continue

                    try:
                        meat_type = MeatTypes.objects.get(name=sanitized(record["meat type"]))
                    except MeatTypes.DoesNotExist:
                        meat_type = MeatTypes()
                        meat_type.name = sanitized(record["meat type"])
                        meat_type.save()
                    except Exception as e:
                        out_file.write(f"\n Meat type data is not loaded."
                                       f"at line {idx + 1}:  {record['meat type']} . Error was:  {e}")
                        self.logger.warning(f"\n Meat type data is not loaded."
                                       f"at line {idx + 1}:  {record['meat type']} . Error was:  {e}")
                        continue

                    try:
                        meal_type = MealTypes.objects.get(name=sanitized(record["meal type"]))
                    except MealTypes.DoesNotExist:
                        meal_type = MealTypes()
                        meal_type.name = sanitized(record["meal type"])
                        meal_type.save()
                    except Exception as e:
                        out_file.write(f"\n Meal type data is not loaded."
                                       f"at line {idx + 1}:  {record['meal type']} . Error was:  {e}")
                        self.logger.warning(f"\n Meal type data is not loaded."
                                       f"at line {idx + 1}:  {record['meal type']} . Error was:  {e}")
                        continue

        htmlgen = f'Hi, There is a update to your upload ingredient report.'
        send_email("Load Pre-requisite to Recipe", htmlgen, output_file, self.recipient)
        os.remove(output_file)

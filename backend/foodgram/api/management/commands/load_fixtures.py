import json
import os

from django.core.management.base import BaseCommand

from api.models import Ingredient, Unit


class Command(BaseCommand):
    help = "Help me please"

    def handle(self, *args, **kwargs):
        fixture_path = os.path.join(
            'api', 'management', 'commands', 'ingredients.json'
        )
        self.load_json(fixture_path)

    def load_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            ingredients = []
            for item in data:
                unit_title = item['measurement_unit']
                unit, created = Unit.objects.get_or_create(title=unit_title)

                ingredients.append(
                    Ingredient(
                        name=item['name'],
                        measurement_unit=unit
                    )
                )
            Ingredient.objects.bulk_create(ingredients)
        self.stdout.write(self.style.SUCCESS('Successfully loaded JSON data'))

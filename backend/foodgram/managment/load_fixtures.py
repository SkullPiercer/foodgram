import csv
import json

from django.core.management.base import BaseCommand
from django.core.serializers import deserialize

from api.models import Ingredient

class Command(BaseCommand):
    help = 'Load fixtures from CSV and JSON files'

    def handle(self, *args, **kwargs):
        self.load_json('path/to/your/ingredients.json')
        self.load_csv('path/to/your/ingredients.csv')

    def load_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for obj in deserialize('json', json.dumps(data)):
                obj.save()
        self.stdout.write(self.style.SUCCESS('Successfully loaded JSON data'))

    def load_csv(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Ingredient.objects.create(**row)
        self.stdout.write(self.style.SUCCESS('Successfully loaded CSV data'))

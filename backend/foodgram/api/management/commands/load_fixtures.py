import json

from django.core.management.base import BaseCommand
from django.core.serializers import deserialize


class Command(BaseCommand):
    help = "Help me please"

    def handle(self, *args, **kwargs):
        self.load_json('ingredients.json')

    def load_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for obj in deserialize('json', json.dumps(data)):
                obj.save()
        self.stdout.write(self.style.SUCCESS('Successfully loaded JSON data'))
#123
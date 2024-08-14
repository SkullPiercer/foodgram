from django.core.validators import RegexValidator
from rest_framework import serializers

username_validator = RegexValidator(
    regex=r'^[\w.@+-]+\Z',
    message='Invalid characters in username',
    code='invalid_username'
)


def validate_tags(tags_data):
    from .models import Tag
    if tags_data is None:
        raise serializers.ValidationError(
          {'tags': 'Укажите теги.'}
        )

    if len(tags_data) == 0 or len(set(tags_data)) < len(tags_data):
        raise serializers.ValidationError(
          {'tags': 'Неверно указаны теги.'}
        )

    for tag in tags_data:
        if not Tag.objects.filter(id=tag).exists():
            raise serializers.ValidationError(
              {'tags': 'Несуществующий тег.'}
            )

    return tags_data


def validate_cooking_time(time):
    if time < 1:
        raise serializers.ValidationError(
          {'cooking_time': 'Невозможное время приготовления.'}
        )


def validate_ingredients(ingredient_list):
    if ingredient_list is None or len(ingredient_list) == 0:
        raise serializers.ValidationError(
          {'ingredients': 'Неверно переданы ингредиенты!'}
        )

    unique_ingredients = set()
    for ingredient in ingredient_list:
        unique_ingredients.add(ingredient['id'])
        if ingredient['amount'] < 1:
            raise serializers.ValidationError(
              {'ingredients': 'Неверно передано кол-во ингредиентов!'}
            )

    if len(unique_ingredients) < len(ingredient_list):
        raise serializers.ValidationError(
          {'ingredients': 'Переданы одинаковые ингредиенты!'}
        )

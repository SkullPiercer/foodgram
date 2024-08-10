from django.core.validators import RegexValidator
from rest_framework import serializers

username_validator = RegexValidator(
    regex=r'^[\w.@+-]+\Z',
    message='Invalid characters in username',
    code='invalid_username'
)


def validate_tags(tags_data):
    from .models import Tag
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


from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Ingredient, Tag

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'title', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Ingredient
        fields = ('id', 'title', 'measurement_unit')


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
        write_only_fields = ('password',)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

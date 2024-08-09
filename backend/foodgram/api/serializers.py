import base64

from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db import transaction

from .models import Ingredient, Recipe, RecipeIngredients, Subscribe, Tag, \
    Favorite
from .validators import username_validator

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.CharField(source='measurement_unit.title',
                                             read_only=True)
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']
        read_only_fields = ['id']
        extra_kwargs = {'measurement_unit': {'read_only': True}}


# Подумать надо ли разделить создание, удаление и список на разные сирики
class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ('subscriber', 'subscribed_to')

    def validate(self, data):
        subscriber = data['subscriber']
        subscribed_to = data['subscribed_to']

        if subscriber == subscribed_to:
            raise serializers.ValidationError(
                "Нельзя подписаться на себя!")

        if Subscribe.objects.filter(subscriber=subscriber,
                                    subscribed_to=subscribed_to).exists():
            raise serializers.ValidationError(
                "Вы уже подписаны на этого пользователя!")
        return data


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def validate(self, data):
        if not data.get('avatar'):
            raise serializers.ValidationError(
                {'avatar': 'Поле не может быть пустым!'})
        return data


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=(username_validator,)
    )
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request', None)
        if request is None or request.user.is_anonymous or request.user == obj:
            return False
        return Subscribe.objects.filter(subscribed_to=obj,
                                        subscriber=request.user).exists()


class IngredientAmountSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)

    class Meta:
        model = RecipeIngredients
        exclude = ['recipe']


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)

    def get_ingredients(self, obj):
        ingredients = IngredientAmountSerializer(
            RecipeIngredients.objects.filter(recipe=obj), many=True
        ).data
        format_ingredients = []
        for ingredient in ingredients:
            formatted_ingredient = {
                'id': ingredient['ingredient']['id'],
                'amount': ingredient['amount'],
                'name': ingredient['ingredient']['name'],
                'measurement_unit': ingredient['ingredient']['measurement_unit']
            }
            format_ingredients.append(formatted_ingredient)
        return format_ingredients

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'image',
            'text',
            'name',
            'cooking_time'
        )


class RecipeCreateSerializer(RecipeSerializer):
    image = Base64ImageField(required=True)
    cooking_time = serializers.IntegerField(
        required=True, )
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'image',
            'text',
            'name',
            'cooking_time'
        )
        read_only_fields = ('author',)

    def validate(self, data):
        data = super().validate(data)
        request = self.context['request']
        tags_data = request.data.get('tags')
        ingredients_data = request.data.get('ingredients')
        unique_ingredients = set()
        new_ingredients_data = []
        for ingredient_data in ingredients_data:
            unique_ingredients.add(ingredient_data['id'])
            try:
                ingredients = Ingredient.objects.filter(
                    id__in=unique_ingredients)
                new_ingredients_data.append(
                    {
                        'ingredient': ingredients.get(
                            pk=ingredient_data['id']),
                        'amount': ingredient_data['amount']
                    }
                )
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    {'ingredients': ['Несуществующий ингредиент.']}
                )
            data['ingredients'] = new_ingredients_data
            data['tags'] = tags_data
        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)

        for _ in tags:
            recipe.tags.set(tags)

        for ingredient_data in ingredients_data:
            ingredient = ingredient_data['ingredient']
            amount = ingredient_data['amount']

            RecipeIngredients.objects.create(
                ingredient_id=ingredient.id,
                recipe_id=recipe.id,
                amount=amount

            )

        return recipe


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ('recipe',)

    def validate(self, data):
        user = self.context['request'].user
        recipe_id = self.context['view'].kwargs.get('id')

        if Favorite.objects.filter(user=user, recipe_id=recipe_id).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже добавлен в избранное.')

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        recipe_id = self.context['view'].kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        favorite = Favorite.objects.create(user=user, recipe=recipe)
        return favorite

    def to_representation(self, instance):
        recipe = instance.recipe
        return {
            'id': recipe.id,
            'name': recipe.name,
            'image': recipe.image.url,
            'cooking_time': recipe.cooking_time
        }

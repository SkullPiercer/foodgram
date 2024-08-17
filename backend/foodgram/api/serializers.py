import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django_short_url.views import get_surl
from rest_framework import serializers

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredients,
    Subscribe,
    Tag,
    ShopList
)
from .mixins import RecipeMixin

from .validators import (
    username_validator,
    validate_cooking_time,
    validate_ingredients,
    validate_tags,
)

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
    measurement_unit = serializers.CharField(
        source='measurement_unit.title',
        read_only=True
    )

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']
        read_only_fields = ['id']
        extra_kwargs = {'measurement_unit': {'read_only': True}}


class RecipeMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ('subscriber', 'subscribed_to')
        read_only_fields = ('subscriber', 'subscribed_to')

    def validate(self, data):
        subscriber = self.context['request'].user
        subscribed_to_id = self.context['view'].kwargs.get('id')
        subscribed_to = get_object_or_404(User, pk=subscribed_to_id)

        if subscriber == subscribed_to:
            raise serializers.ValidationError('Нельзя подписаться на себя!')

        if subscriber.subscriber.filter(subscribed_to=subscribed_to).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя!'
            )

        data['subscriber'] = subscriber
        data['subscribed_to'] = subscribed_to
        return data

    def to_representation(self, instance):
        user = instance.subscribed_to
        return SubscribeListSerializer(user, context=self.context).data


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
        request = self.context.get('request')
        if request is None or request.user.is_anonymous or request.user == obj:
            return False
        return obj.subscribed_to.filter(subscriber=request.user).exists()


class SubscribeListSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        limit = self.context['request'].GET.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeMiniSerializer(recipes, many=True, read_only=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class IngredientAmountSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)

    class Meta:
        model = RecipeIngredients
        exclude = ('recipe',)


class RecipeSerializer(serializers.ModelSerializer, RecipeMixin):
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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
                'measurement_unit': ingredient['ingredient'][
                    'measurement_unit']
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
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )


class RecipeCreateSerializer(RecipeSerializer, RecipeMixin):
    image = Base64ImageField(required=True)
    cooking_time = serializers.IntegerField(required=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )
        read_only_fields = ('author', 'is_favorited', 'is_in_shopping_cart',)

    @staticmethod
    def create_ingredients(ingredients_data, recipe_id):
        recipe_ingredients = []

        for ingredient_data in ingredients_data:
            ingredient = ingredient_data['ingredient']
            amount = ingredient_data['amount']

            recipe_ingredients.append(
                RecipeIngredients(
                    ingredient_id=ingredient.id,
                    recipe_id=recipe_id,
                    amount=amount
                )
            )
        return recipe_ingredients

    def validate(self, data):
        data = super().validate(data)
        request = self.context['request']
        tags_data = request.data.get('tags')
        ingredients_data = request.data.get('ingredients')
        unique_ingredients = set()
        new_ingredients_data = []

        validate_tags(tags_data)
        validate_ingredients(ingredients_data)
        validate_cooking_time(request.data.get('cooking_time'))

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
        recipe.tags.set(tags)
        recipe_ingredients = self.create_ingredients(ingredients_data,
                                                     recipe.id)
        RecipeIngredients.objects.bulk_create(recipe_ingredients)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        instance.ingredients.clear()
        instance.tags.set(tags)
        recipe_ingredients = self.create_ingredients(ingredients_data,
                                                     instance.id)
        RecipeIngredients.objects.bulk_create(recipe_ingredients)

        return super().update(instance, validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ('recipe',)

    def validate(self, data):
        user = self.context['request'].user
        recipe_id = self.context['view'].kwargs.get('id')

        if user.favorites.filter(recipe__id=recipe_id).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже добавлен в избранное.'
            )

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        recipe_id = self.context['view'].kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        return Favorite.objects.create(user=user, recipe=recipe)

    def to_representation(self, instance):
        recipe = instance.recipe
        return {
            'id': recipe.id,
            'name': recipe.name,
            'image': recipe.image.url,
            'cooking_time': recipe.cooking_time
        }


class ShopListSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(read_only=True)

    class Meta:
        model = ShopList
        fields = ('recipe',)

    def validate(self, data):
        user = self.context['request'].user
        recipe_id = self.context['view'].kwargs.get('id')

        if user.shop_user.filter(recipe__id=recipe_id).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже добавлен в список покупок.'
            )
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        recipe_id = self.context['view'].kwargs.get('id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        return ShopList.objects.create(user=user, recipe=recipe)

    def to_representation(self, instance):
        recipe = instance.recipe
        return {
            'id': recipe.id,
            'name': recipe.name,
            'image': recipe.image.url,
            'cooking_time': recipe.cooking_time
        }


class ShortURLSerializer(serializers.ModelSerializer):
    short_url = serializers.SerializerMethodField(source='short-link')

    class Meta:
        model = Recipe
        fields = ('short_url',)

    def get_short_url(self, obj):
        request = self.context.get('request')
        if request and request.resolver_match:
            recipe_id = request.resolver_match.kwargs.get('id')
            surl = get_surl(f"/api/recipes/{recipe_id}/")
            return f'{request.scheme}://{request.get_host()}{surl}'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['short-link'] = representation.pop('short_url')
        return representation

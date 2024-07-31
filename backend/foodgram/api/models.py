from django.db import models

from users.models import User


class Unit(models.Model):
    title = models.CharField(max_length=30)


class Ingredient(models.Model):
    title = models.CharField(max_length=100)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)


class Tag(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.SmallIntegerField(default=0)


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    image = models.ImageField(upload_to='recipes/')
    description = models.TextField(max_length=2000)
    ingredients = models.ManyToManyField(
        Ingredient,
        through=RecipeIngredients
    )
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveIntegerField()
    in_favorites = models.BooleanField(default=False)
    in_shop_list = models.BooleanField(default=False)

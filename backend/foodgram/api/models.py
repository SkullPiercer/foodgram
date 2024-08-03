from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name'
    )

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
        error_messages={
            'unique': 'This email already taken'
        }
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        unique=True,
        error_messages={
            'unique': 'This username already taken'
        }
    )

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150
    )

    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150
    )

    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.username


class Unit(models.Model):
    title = models.CharField(max_length=30)

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    title = models.CharField(max_length=100)
    measurement_unit = models.ForeignKey(Unit, on_delete=models.CASCADE)


class Tag(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.SmallIntegerField(default=0)


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        related_name='recipes',
        on_delete=models.CASCADE
    )
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

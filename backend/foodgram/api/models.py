from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import username_validator


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
            'unique': 'Этот адрес эл.почты уже занят!'
        },
        blank=False,
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        unique=True,
        error_messages={
            'unique': 'Имя пользователя уже занято!'
        },
        max_length=150,
        validators=[username_validator],
        blank=False,
    )

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=False,
    )

    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=False,
    )

    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Unit(models.Model):
    title = models.CharField(max_length=30, verbose_name='Название')

    class Meta:
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'
        ordering = ('title',)

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    measurement_unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        verbose_name='Единица измерения',
        related_name='measurement_unit',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipes'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredients'
    )
    amount = models.PositiveSmallIntegerField(default=0, verbose_name='Кол-во')

    class Meta:
        verbose_name = 'Рецепт/Ингредиент'
        verbose_name_plural = 'Рецепты/Ингредиенты'
        ordering = ('recipe', 'ingredient')

    def __str__(self):
        return f'{self.recipe} / {self.ingredient}'


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        related_name='recipes',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=256, verbose_name='Название')
    image = models.ImageField(upload_to='recipes/', verbose_name='Картинка')
    text = models.TextField(max_length=2000, verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through=RecipeIngredients,
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления'
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создано в')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created',)

    def __str__(self):
        return self.name


class Subscribe(models.Model):
    subscriber = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    subscribed_to = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscribed_to',
        verbose_name='Подписан на'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('subscriber', 'subscribed_to')

    def __str__(self):
        return f'Подписка пользователя {self.subscriber}'


class Favorite(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        ordering = ('user', 'recipe')

    def __str__(self):
        return f'Избранное пользователя {self.user}'


class ShopList(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shop_user',
        verbose_name='Пользователь'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shop_recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ('user', 'recipe')

    def __str__(self):
        return f'Список покупок пользователя {self.user}'

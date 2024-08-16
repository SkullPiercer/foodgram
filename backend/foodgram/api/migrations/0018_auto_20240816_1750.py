# Generated by Django 3.2 on 2024-08-16 12:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_auto_20240816_1744'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'ordering': ('user', 'recipe'), 'verbose_name': 'Избранное', 'verbose_name_plural': 'Избранные'},
        ),
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ('name',), 'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='recipeingredients',
            options={'ordering': ('recipe', 'ingredient'), 'verbose_name': 'Рецепт/Ингредиент', 'verbose_name_plural': 'Рецепты/Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='shoplist',
            options={'ordering': ('user', 'recipe'), 'verbose_name': 'Список покупок', 'verbose_name_plural': 'Списки покупок'},
        ),
        migrations.AlterModelOptions(
            name='subscribe',
            options={'ordering': ('subscriber', 'subscribed_to'), 'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ('name',), 'verbose_name': 'Тег', 'verbose_name_plural': 'Теги'},
        ),
        migrations.AlterModelOptions(
            name='unit',
            options={'ordering': ('title',), 'verbose_name': 'Единица измерения', 'verbose_name_plural': 'Единицы измерения'},
        ),
    ]

# Generated by Django 3.2 on 2024-08-14 17:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_auto_20240814_1953'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='in_favorites',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='in_shop_list',
        ),
    ]

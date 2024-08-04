# Generated by Django 3.2 on 2024-08-04 11:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_customuser_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(error_messages={'unique': 'This username already taken'}, max_length=150, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_username', message='Invalid characters in username', regex='^[\\w.@+-]+\\Z')], verbose_name='Имя пользователя'),
        ),
    ]

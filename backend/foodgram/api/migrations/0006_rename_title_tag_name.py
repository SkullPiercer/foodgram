# Generated by Django 3.2 on 2024-08-04 12:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_customuser_username'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tag',
            old_name='title',
            new_name='name',
        ),
    ]

# Generated by Django 3.2 on 2023-08-08 21:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20230804_1338'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'User'},
        ),
    ]

# Generated by Django 3.2.4 on 2021-08-11 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('createteam', '0013_league_allowed_to_create_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='league',
            name='end_date',
            field=models.DateTimeField(),
        ),
    ]

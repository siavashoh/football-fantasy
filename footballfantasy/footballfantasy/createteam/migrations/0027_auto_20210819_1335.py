# Generated by Django 3.2.4 on 2021-08-19 09:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('createteam', '0026_auto_20210819_1331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='league',
            name='allowed_to_create_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='league',
            name='next_change_format_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 8, 19, 13, 35, 33, 325212)),
        ),
    ]

# Generated by Django 3.2.4 on 2021-08-19 09:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('createteam', '0027_auto_20210819_1335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='league',
            name='next_change_format_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 8, 19, 13, 41, 23, 998229)),
        ),
    ]

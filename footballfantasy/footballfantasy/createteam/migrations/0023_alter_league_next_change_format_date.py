# Generated by Django 3.2.4 on 2021-08-17 11:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('createteam', '0022_alter_league_next_change_format_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='league',
            name='next_change_format_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 8, 17, 16, 9, 22, 104488)),
        ),
    ]

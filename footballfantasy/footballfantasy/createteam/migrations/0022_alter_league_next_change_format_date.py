# Generated by Django 3.2.4 on 2021-08-17 11:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('createteam', '0021_auto_20210817_1609'),
    ]

    operations = [
        migrations.AlterField(
            model_name='league',
            name='next_change_format_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 8, 17, 16, 9, 19, 936094)),
        ),
    ]

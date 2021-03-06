# Generated by Django 3.2.4 on 2021-08-23 11:28

import datetime
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('createteam', '0032_alter_league_next_change_format_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='league',
            old_name='allowed_to_change_format',
            new_name='allow_to_change_format',
        ),
        migrations.AddField(
            model_name='league',
            name='allow_to_change_format_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='league',
            name='next_change_format_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 8, 23, 15, 58, 11, 461577)),
        ),
    ]

# Generated by Django 3.2.4 on 2021-08-29 05:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0014_alter_log_create_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='create_at',
            field=models.DateTimeField(default=datetime.datetime(2021, 8, 29, 9, 57, 36, 858176)),
        ),
    ]

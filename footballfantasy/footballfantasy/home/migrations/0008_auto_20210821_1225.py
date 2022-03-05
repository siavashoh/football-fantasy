# Generated by Django 3.2.4 on 2021-08-21 07:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_auto_20210819_1647'),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('message', models.CharField(max_length=500)),
                ('data', models.JSONField()),
                ('create_at', models.DateTimeField(default=datetime.datetime(2021, 8, 21, 12, 25, 36, 275406))),
                ('is_info', models.BooleanField(default=False)),
                ('is_error', models.BooleanField(default=False)),
                ('is_warning', models.BooleanField(default=False)),
            ],
        ),
        migrations.DeleteModel(
            name='Logs',
        ),
    ]

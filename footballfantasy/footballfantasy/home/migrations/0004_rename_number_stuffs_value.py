# Generated by Django 3.2.4 on 2021-07-27 11:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_auto_20210727_1618'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stuffs',
            old_name='number',
            new_name='value',
        ),
    ]

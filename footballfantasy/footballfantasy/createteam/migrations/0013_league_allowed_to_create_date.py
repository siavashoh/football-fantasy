# Generated by Django 3.2.4 on 2021-08-11 11:56

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('createteam', '0012_user_team_change_number_of_changes_allowed'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='allowed_to_create_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]

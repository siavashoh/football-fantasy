# Generated by Django 3.2.4 on 2021-06-17 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_userprofile_is_email_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_team_created',
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 3.2.4 on 2021-07-29 12:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('createteam', '0009_alter_team_player_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='User_team_change',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('first_team', models.JSONField()),
                ('second_team', models.JSONField()),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='createteam.league')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

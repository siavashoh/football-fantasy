# Generated by Django 3.2.4 on 2021-07-04 13:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('createteam', '0006_alter_player_team'),
    ]

    operations = [
        migrations.RenameField(
            model_name='team_player',
            old_name='Team_id',
            new_name='Team',
        ),
        migrations.RenameField(
            model_name='team_player',
            old_name='player_id',
            new_name='player',
        ),
    ]

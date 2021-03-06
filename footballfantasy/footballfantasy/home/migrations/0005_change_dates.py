# Generated by Django 3.2.4 on 2021-08-03 05:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('createteam', '0011_player_team_name'),
        ('home', '0004_rename_number_stuffs_value'),
    ]

    operations = [
        migrations.CreateModel(
            name='Change_Dates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_ch_15', models.DateTimeField()),
                ('end_ch_15', models.DateTimeField()),
                ('start_ch_5', models.DateTimeField()),
                ('end_ch_5', models.DateTimeField()),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='createteam.league')),
            ],
        ),
    ]

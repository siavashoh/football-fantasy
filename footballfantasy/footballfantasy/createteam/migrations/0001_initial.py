# Generated by Django 3.2.4 on 2021-06-06 13:08

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=50)),
                ('lastname', models.CharField(max_length=50)),
                ('team', models.CharField(max_length=50)),
                ('post', models.CharField(max_length=50)),
                ('score', models.FloatField(blank=True, default='0')),
                ('image_file_name', models.CharField(blank=True, max_length=50, null=True)),
                ('user', models.ManyToManyField(related_name='User_Player', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['firstname', 'lastname'],
            },
        ),
    ]

# Generated by Django 5.1.3 on 2025-03-09 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0014_player_bat_speed_player_batting_player_birthdate_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='last_league',
            field=models.CharField(blank=True, max_length=225),
        ),
    ]

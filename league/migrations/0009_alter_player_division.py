# Generated by Django 5.1.3 on 2025-03-07 10:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0008_alter_draftpick_division_alter_player_division_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='division',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='players', to='league.division'),
        ),
    ]

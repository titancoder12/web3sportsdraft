# Generated by Django 5.1.3 on 2025-03-19 09:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('league', '0018_player_teams'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_id', models.CharField(max_length=50, unique=True)),
                ('date', models.DateTimeField()),
                ('time', models.TimeField()),
                ('location', models.CharField(max_length=100)),
                ('finalized', models.BooleanField(default=False)),
                ('is_verified', models.BooleanField(default=False)),
                ('team_away', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='away_games', to='league.team')),
                ('team_home', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='home_games', to='league.team')),
            ],
        ),
        migrations.CreateModel(
            name='PlayerGameStat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('at_bats', models.IntegerField(default=0)),
                ('runs', models.IntegerField(default=0)),
                ('hits', models.IntegerField(default=0)),
                ('rbis', models.IntegerField(default=0)),
                ('singles', models.IntegerField(default=0)),
                ('doubles', models.IntegerField(default=0)),
                ('triples', models.IntegerField(default=0)),
                ('home_runs', models.IntegerField(default=0)),
                ('strikeouts', models.IntegerField(default=0)),
                ('base_on_balls', models.IntegerField(default=0)),
                ('hit_by_pitch', models.IntegerField(default=0)),
                ('sacrifice_flies', models.IntegerField(default=0)),
                ('innings_pitched', models.FloatField(default=0)),
                ('hits_allowed', models.IntegerField(default=0)),
                ('runs_allowed', models.IntegerField(default=0)),
                ('earned_runs', models.IntegerField(default=0)),
                ('walks_allowed', models.IntegerField(default=0)),
                ('strikeouts_pitching', models.IntegerField(default=0)),
                ('home_runs_allowed', models.IntegerField(default=0)),
                ('is_verified', models.BooleanField(default=False)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='league.game')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='league.player')),
            ],
        ),
    ]

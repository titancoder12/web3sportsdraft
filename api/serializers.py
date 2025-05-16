from rest_framework import serializers
from league.models import *
from django.contrib.auth.models import User


class TeamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'players']

class LeagueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = League
        fields = ['id', 'name', 'description', 'divisions']

class DivisionSerializer(serializers.HyperlinkedModelSerializer):
    league = serializers.PrimaryKeyRelatedField(queryset=League.objects.all())
    class Meta:
        model = Division
        fields = ['id', 'name', 'league', 'teams']

class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    class Meta:
        model = Player
        fields = ['id', 'first_name', 'last_name', 'division', 'teams', 'user']

class GameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'game_id', 'date', 'time', 'location', 'team_home', 'team_away', 'finalized', 'is_verified']

class PlayerGameStatSerializer(serializers.HyperlinkedModelSerializer):
    submitted_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    class Meta:
        model = PlayerGameStat
        fields = ['id', 'player', 'game', 'at_bats', 'runs', 'hits', 'rbis', 'singles', 'doubles', 'triples', 
                 'home_runs', 'strikeouts', 'base_on_balls', 'hit_by_pitch', 'sacrifice_flies', 'innings_pitched',
                 'hits_allowed', 'runs_allowed', 'earned_runs', 'walks_allowed', 'strikeouts_pitching',
                 'home_runs_allowed', 'is_verified', 'submitted_by']

class FairPlayRuleSetSerializer(serializers.HyperlinkedModelSerializer):
    league = serializers.PrimaryKeyRelatedField(queryset=League.objects.all())
    class Meta:
        model = FairPlayRuleSet
        fields = ['id', 'league', 'age_group', 'min_innings_per_player', 'max_consecutive_bench_innings',
                 'min_plate_appearances', 'enforce_plate_appearance', 'enforce_position_rotation',
                 'max_innings_per_position', 'eh_option_start_date', 'eh_option_end_date',
                 'no_mandated_fair_play']

class LineupPlanSerializer(serializers.HyperlinkedModelSerializer):
    coach = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = LineupPlan
        fields = ['id', 'team', 'game', 'coach', 'created_at', 'updated_at', 'is_final', 'notes']
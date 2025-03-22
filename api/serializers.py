from rest_framework import serializers
from league.models import *
from django.contrib.auth.models import User


class TeamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'players']

class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    #teams = serializers.PrimaryKeyRelatedField(many=True, queryset=Team.objects.all())
    class Meta:
        model = Player
        fields = ['id', 'first_name', 'last_name','teams','team','division']

class DivisionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Division
        fields = ['id', 'name', 'league']

class GameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Game
        fields = ['id','game_id','team_home', 'team_away','date','time','location','finalized','is_verified']

class PlayerGameStatSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PlayerGameStat
        fields = ['id','player','game','at_bats','runs','hits','rbis','singles','doubles','triples','home_runs','strikeouts','base_on_balls','hit_by_pitch','sacrifice_flies','innings_pitched','hits_allowed','runs_allowed','earned_runs','walks_allowed','strikeouts_pitching','home_runs_allowed','is_verified']
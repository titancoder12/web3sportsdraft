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
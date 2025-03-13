from rest_framework import serializers
from league.models import *
from django.contrib.auth.models import User

class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'first_name','last_name', 'birthdate']
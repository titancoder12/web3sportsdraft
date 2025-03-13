from django.shortcuts import render
from rest_framework import viewsets
from .serializers import *
from league.models import *
from .serializers import *
from rest_framework import permissions

# Create your views here.
class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [permissions.IsAuthenticated]
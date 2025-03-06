# league/admin.py
from django.contrib import admin
from .models import Team, Player, DraftPick

admin.site.register(Team)
admin.site.register(Player)
admin.site.register(DraftPick)
# league/admin.py
from django.contrib import admin
from .models import Team, Player, DraftPick

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    filter_horizontal = ('coaches',)  # Nicer UI for ManyToManyField

admin.site.register(Player)
admin.site.register(DraftPick)
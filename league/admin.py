# league/admin.py
from django.contrib import admin
from .models import Team, Player, DraftPick

admin.site.site_title = "Baseball League Admin"
admin.site.site_header = "Baseball League Admin"
admin.site.index_title = "Welcome to Baseball League Admin"

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    filter_horizontal = ('coaches',)

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'position', 'rating', 'team', 'user', 'description', 'coach_comments')
    list_filter = ('team',)
    search_fields = ('name', 'description', 'coach_comments')

admin.site.register(DraftPick)
# league/admin.py
from django.contrib import admin
from .models import League, Division, Team, Player, DraftPick

admin.site.site_title = "Baseball League Admin"
admin.site.site_header = "Baseball League Admin"
admin.site.index_title = "Welcome to Baseball League Admin"

@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name',)

# league/admin.py
@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'league', 'is_open')
    list_filter = ('league', 'is_open')
    filter_horizontal = ('coordinators',)  # For easy coordinator assignment

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'division')
    filter_horizontal = ('coaches',)
    list_filter = ('division',)

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('first_name','last_name', 'age', 'position', 'rating', 'team', 'user', 'description', 'coach_comments')
    list_filter = ('team',)
    search_fields = ('first_name','last_name', 'description', 'coach_comments')

@admin.register(DraftPick)
class DraftPickAdmin(admin.ModelAdmin):
    list_display = ('division', 'team', 'player', 'pick_number', 'round_number')
    list_filter = ('division',)
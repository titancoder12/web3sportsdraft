# league/admin.py
from django.contrib import admin
from .models import League, Division, Team, Player, DraftPick, SignInLog, Game


admin.site.site_title = "Baseball League Admin"
admin.site.site_header = "Baseball League Admin"
admin.site.index_title = "Welcome to Baseball League Admin"

@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'league', 'is_open')
    list_filter = ('league', 'is_open')
    filter_horizontal = ('coordinators',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'division')
    filter_horizontal = ('coaches',)
    list_filter = ('division',)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('team_home', 'team_away', 'date', 'time', 'location', 'finalized', 'is_verified')
    list_filter = ('finalized', 'is_verified', 'date')
    search_fields = ('team_home__name', 'team_away__name', 'location')

# Custom method to display teams in list_display
def player_teams(obj):
    return ", ".join(team.name for team in obj.teams.all()) if obj.teams.exists() else "No Teams"
player_teams.short_description = "Teams"

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'age', 'position', 'rating', 'team', player_teams, 'user', 'description', 'coach_comments')
    list_filter = ('team',)  # Keep team for now; add teams filter later if needed
    search_fields = ('first_name', 'last_name', 'description', 'coach_comments')
    # Optional: Add teams to the form view
    filter_horizontal = ('teams',)

@admin.register(DraftPick)
class DraftPickAdmin(admin.ModelAdmin):
    list_display = ('division', 'team', 'player', 'pick_number', 'round_number')
    list_filter = ('division',)

@admin.register(SignInLog)
class SigninLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp')
    list_filter = ('timestamp', 'user')
    search_fields = ('user__username', 'user__email')
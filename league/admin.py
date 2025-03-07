# league/admin.py
from django.contrib import admin
from .models import Team, Player, DraftPick

# Customize the admin site
admin.site.site_title = "Web3Sports Draft"  # Browser tab title
admin.site.site_header = "Web3Sports Draft Admin"  # Header on the admin page
admin.site.index_title = "Welcome Web3Sports Draft Admin"  # Title on the admin index page

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    filter_horizontal = ('coaches',)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'position', 'rating', 'team', 'user')
    list_filter = ('team',)
    search_fields = ('name',)

admin.site.register(DraftPick)
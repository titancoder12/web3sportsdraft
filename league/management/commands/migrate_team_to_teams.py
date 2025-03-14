# league/management/commands/migrate_team_to_teams.py
from django.core.management.base import BaseCommand
from league.models import Player

class Command(BaseCommand):
    help = 'Migrate Player.team ForeignKey data to Player.teams ManyToManyField'

    def handle(self, *args, **options):
        migrated_count = 0
        for player in Player.objects.all():
            if player.team and not player.teams.filter(id=player.team.id).exists():
                player.teams.add(player.team)
                migrated_count += 1
                self.stdout.write(self.style.SUCCESS(f"Migrated {player} to team {player.team}"))
        self.stdout.write(self.style.SUCCESS(f"Completed migration: {migrated_count} players updated"))
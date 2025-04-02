from django.core.management.base import BaseCommand
from league.models import Player, PerformanceEvaluation

class Command(BaseCommand):
    help = "Copy evaluation fields from Player model to PerformanceEvaluation if not already migrated."

    def handle(self, *args, **options):
        migrated = 0
        skipped = 0

        for player in Player.objects.all():
            if player.evaluations.exists():
                self.stdout.write(self.style.WARNING(f"⏭ Player {player} already has evaluations. Skipping."))
                skipped += 1
                continue

            # Only copy if there's at least one value present
            if any([
                player.grip_strength, player.lateral_jump, player.shot_put,
                player.five_ten_five_yards, player.ten_yards, player.catcher_pop,
                player.fielding_notes, player.exit_velo, player.bat_speed, player.pitching_comment
            ]):
                PerformanceEvaluation.objects.create(
                    player=player,
                    grip_strength=player.grip_strength,
                    lateral_jump=player.lateral_jump,
                    shot_put=player.shot_put,
                    five_ten_five_yards=player.five_ten_five_yards,
                    ten_yards=player.ten_yards,
                    catcher_pop=player.catcher_pop,
                    fielding_notes=player.fielding_notes,
                    exit_velo=player.exit_velo,
                    bat_speed=player.bat_speed,
                    pitching_comment=player.pitching_comment,
                )
                self.stdout.write(self.style.SUCCESS(f"✅ Created evaluation for {player.first_name} {player.last_name}"))
                migrated += 1
            else:
                self.stdout.write(self.style.WARNING(f"⚠️  Player {player} has no data to migrate. Skipping."))

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Migration complete: {migrated} migrated, {skipped} skipped."))

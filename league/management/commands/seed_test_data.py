from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from league.models import Team, Player, Division, Game, League
from datetime import datetime
import uuid
import random

class Command(BaseCommand):
    help = "Seed the database with test data including real MLB-inspired names."

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Clear existing data before seeding.')

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write("🔄 Resetting existing data...")
            User.objects.exclude(is_superuser=True).delete()
            Player.objects.all().delete()
            Team.objects.all().delete()
            Division.objects.all().delete()
            League.objects.all().delete()
            Game.objects.all().delete()

        self.stdout.write("🌱 Seeding data...")

        league_names = ["Pacific League", "Atlantic League"]
        divisions_per_league = 3
        teams_per_division = 6
        players_per_division = 72

        all_divisions = []
        used_names = set()

        first_names = ['Shohei', 'Aaron', 'Mookie', 'Ronald', 'Freddie', 'Jose', 'Juan', 'Fernando', 'Vladimir', 'Julio', 'Mike', 'Bo', 'Corey', 'Yordan', 'Adley', 'Trea']
        last_names = ['Ohtani', 'Judge', 'Betts', 'Acuña', 'Freeman', 'Ramirez', 'Soto', 'Tatis', 'Guerrero', 'Rodriguez', 'Trout', 'Bichette', 'Seager', 'Alvarez', 'Rutschman', 'Turner']
        coach_names = [('Dusty', 'Baker'), ('Terry', 'Francona'), ('Bob', 'Melvin'), ('Bruce', 'Bochy'), ('Dave', 'Roberts'), ('Aaron', 'Boone')]
        coord_names = [('Alex', 'Anthopoulos'), ('Brian', 'Cashman'), ('Farhan', 'Zaidi'), ('James', 'Click'), ('Jed', 'Hoyer'), ('Mike', 'Rizzo')]

        # Create leagues
        league_objs = {}
        for league_name in league_names:
            league_obj, _ = League.objects.get_or_create(name=league_name)
            league_objs[league_name] = league_obj

        player_counter = 1
        for league_name in league_names:
            league = league_objs[league_name]
            for d in range(1, divisions_per_league + 1):
                division_name = f"{league_name} - Division {d}"
                division, _ = Division.objects.get_or_create(name=division_name, league=league)
                all_divisions.append(division)

                teams = [Team.objects.get_or_create(name=f"{division_name} Team {t}", division=division)[0] for t in range(1, teams_per_division + 1)]
                is_drafted = d % 2 == 1

                for _ in range(players_per_division):
                    fn = random.choice(first_names)
                    ln = random.choice(last_names)
                    while (fn, ln) in used_names:
                        fn = random.choice(first_names)
                        ln = random.choice(last_names)
                    used_names.add((fn, ln))
                    username = f"player{player_counter}"
                    user = User.objects.create_user(username=username, password="test1234", email=f"{username}@test.com")
                    player = Player.objects.create(user=user, first_name=fn, last_name=ln, division=division)
                    if is_drafted:
                        player.teams.add(random.choice(teams))
                    player_counter += 1

        # Create superuser
        superuser, created = User.objects.get_or_create(username="eugenelin89", defaults={
            "email": "eugene@example.com", "is_superuser": True, "is_staff": True
        })
        if created:
            superuser.set_password("mounties")
            superuser.save()

        for division in all_divisions:
            division.coordinators.add(superuser)

        for i, (fn, ln) in enumerate(coord_names):
            username = f"coord{i+1}"
            user = User.objects.create_user(username=username, password="test1234", email=f"{username}@test.com")
            for div in all_divisions[i::len(coord_names)]:
                div.coordinators.add(user)

        team_qs = Team.objects.all()
        for i, team in enumerate(team_qs):
            fn, ln = coach_names[i % len(coach_names)]
            username = f"coach{i+1}"
            user = User.objects.create_user(username=username, password="test1234", email=f"{username}@test.com")
            team.coaches.add(user)

        self.stdout.write(self.style.SUCCESS("✅ Database seeded with real-name inspired users and structure."))

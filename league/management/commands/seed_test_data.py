from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from league.models import Team, Player, Division, Game, League
from datetime import datetime
import uuid
import random
import time

class Command(BaseCommand):
    help = "Seed the database with test data using adjustable players and divisions and memory-safe bulk_create."

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Clear existing data before seeding.')
        parser.add_argument('--players', type=int, default=72, help='Number of players per division.')
        parser.add_argument('--divisions', type=int, default=3, help='Number of divisions per league.')

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write("🔄 Resetting existing data...")
            User.objects.exclude(is_superuser=True).delete()
            Player.objects.all().delete()
            Team.objects.all().delete()
            Division.objects.all().delete()
            League.objects.all().delete()
            Game.objects.all().delete()

        players_per_division = options['players']
        divisions_per_league = options['divisions']
        teams_per_division = 6

        self.stdout.write(f"🌱 Seeding {divisions_per_league} divisions per league with {players_per_division} players each...")

        league_names = ["Pacific League", "Atlantic League"]
        all_divisions = []
        used_names = set()

        first_names = ["Shohei", "Aaron", "Mookie", "Ronald", "Freddie", "Jose", "Juan", "Fernando",
                       "Vladimir", "Julio", "Mike", "Bo", "Corey", "Yordan", "Adley", "Trea"]
        last_names = ["Ohtani", "Judge", "Betts", "Acuña", "Freeman", "Ramirez", "Soto", "Tatis",
                      "Guerrero", "Rodriguez", "Trout", "Bichette", "Seager", "Alvarez", "Rutschman", "Turner"]
        coach_names = [("Dusty", "Baker"), ("Terry", "Francona"), ("Bob", "Melvin"),
                       ("Bruce", "Bochy"), ("Dave", "Roberts"), ("Aaron", "Boone")]
        coord_names = [("Alex", "Anthopoulos"), ("Brian", "Cashman"), ("Farhan", "Zaidi"),
                       ("James", "Click"), ("Jed", "Hoyer"), ("Mike", "Rizzo")]

        league_objs = {}
        player_counter = 1

        for league_index, league_name in enumerate(league_names, start=1):
            self.stdout.write(f'📦 Processing League {league_index}/{len(league_names)}: {league_name}')
            league_obj, _ = League.objects.get_or_create(name=league_name)
            league_objs[league_name] = league_obj

        for league_name in league_names:
            league = league_objs[league_name]
            for d in range(1, divisions_per_league + 1):
                start_time = time.time()
                self.stdout.write(f'  🧱 Creating Division {d}/{divisions_per_league} in {league_name}')
                division_name = f"{league_name} - Division {d}"
                division, _ = Division.objects.get_or_create(name=division_name, league=league)
                all_divisions.append(division)

                teams = [Team.objects.get_or_create(name=f"{division_name} Team {t}", division=division)[0] for t in range(1, teams_per_division + 1)]
                is_drafted = d % 2 == 1

                player_objs = []
                user_map = {}
                team_assignment_refs = []

                for p in range(players_per_division):
                    fn = random.choice(first_names)
                    ln = random.choice(last_names)
                    while (fn, ln) in used_names:
                        fn = random.choice(first_names)
                        ln = random.choice(last_names)
                    used_names.add((fn, ln))

                    username = f"{fn.lower()}{ln.lower()}"
                    user = User.objects.create_user(username=username, password="test1234", email=f"{username}@test.com")
                    user_map[username] = user
                    player = Player(user=user, first_name=fn, last_name=ln, division=division)
                    player_objs.append(player)

                    if is_drafted:
                        assigned_team = random.choice(teams)
                        team_assignment_refs.append((username, assigned_team.id))

                    if player_counter % 10 == 0:
                        self.stdout.write(f"      ✅ Prepared player {player_counter}: {fn} {ln}")
                    player_counter += 1

                self.stdout.write("📤 Bulk creating players...")
                Player.objects.bulk_create(player_objs, batch_size=50)
                self.stdout.write("✅ Finished bulk creating players.")

                self.stdout.write('🔄 Refreshing players from DB...')
                players = list(Player.objects.filter(division=division).order_by("-id")[:players_per_division])
                players.reverse()

                through_model = Player.teams.through
                through_objs = [
                    through_model(player_id=player.id, team_id=team_id)
                    for player, (username, team_id) in zip(players, team_assignment_refs)
                ]
                self.stdout.write(f'🔗 Assigning {len(through_objs)} team links via bulk_create...')
                through_model.objects.bulk_create(through_objs, batch_size=50)
                self.stdout.write('✅ Finished assigning teams.')

                elapsed = time.time() - start_time
                self.stdout.write(f"  ⏱️ Finished {division_name} in {elapsed:.2f} seconds")

        superuser, created = User.objects.get_or_create(username="eugenelin89", defaults={
            "email": "eugene@example.com", "is_superuser": True, "is_staff": True
        })
        if created:
            superuser.set_password("mounties")
            superuser.save()

        for division in all_divisions:
            division.coordinators.add(superuser)

        self.stdout.write('🔧 Assigning division coordinators...')
        for i, (fn, ln) in enumerate(coord_names):
            username = f"coord{i+1}"
            user = User.objects.create_user(username=username, password="test1234", email=f"{username}@test.com")
            for div in all_divisions[i::len(coord_names)]:
                div.coordinators.add(user)

        self.stdout.write('🧑‍🏫 Assigning team coaches...')
        team_qs = Team.objects.all()
        for i, team in enumerate(team_qs):
            if i % 10 == 0:
                self.stdout.write(f'  🎽 Processing coach {i + 1}/{len(team_qs)}')
            fn, ln = coach_names[i % len(coach_names)]
            username = f"coach{i+1}"
            user = User.objects.create_user(username=username, password="test1234", email=f"{username}@test.com")
            team.coaches.add(user)

        self.stdout.write(self.style.SUCCESS("✅ Database seeded with fast M2M team assignments and adjustable size."))

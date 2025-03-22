from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from league.models import Team, Player, Division, Game, League
from datetime import datetime
import uuid

class Command(BaseCommand):
    help = "Seed deterministic data using politician names. No randomness."

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

        league_names = ["Pacific League", "Atlantic League"]
        divisions_per_league = 2
        teams_per_division = 5
        players_per_division = 50  # 5 teams * 10 players

        player_names = [('Barack', 'Obama'), ('Joe', 'Biden'), ('Hillary', 'Clinton'), ('Donald', 'Trump'), ('Kamala', 'Harris'), ('George', 'Bush'), ('Bernie', 'Sanders'), ('Nikki', 'Haley'), ('Justin', 'Trudeau'), ('Jagmeet', 'Singh'), ('Pierre', 'Poilievre'), ('Chrystia', 'Freeland'), ('Doug', 'Ford'), ('Erin', "O'Toole"), ('Emmanuel', 'Macron'), ('Angela', 'Merkel'), ('Rishi', 'Sunak'), ('Volodymyr', 'Zelenskyy'), ('Narendra', 'Modi'), ('Xi', 'Jinping'), ('Winston', 'Churchill'), ('Franklin', 'Roosevelt'), ('Theodore', 'Roosevelt'), ('Abraham', 'Lincoln'), ('John', 'Kennedy'), ('Lyndon', 'Johnson'), ('Richard', 'Nixon'), ('Gerald', 'Ford'), ('Jimmy', 'Carter'), ('Ronald', 'Reagan'), ('George', 'Washington'), ('Thomas', 'Jefferson'), ('Alexander', 'Hamilton'), ('Benjamin', 'Franklin'), ('John', 'Adams'), ('Andrew', 'Jackson'), ('James', 'Madison'), ('Ulysses', 'Grant'), ('Woodrow', 'Wilson'), ('Herbert', 'Hoover'), ('Harry', 'Truman'), ('Calvin', 'Coolidge'), ('Grover', 'Cleveland'), ('Chester', 'Arthur'), ('Martin', 'Van Buren'), ('Millard', 'Fillmore'), ('James', 'Garfield'), ('William', 'McKinley'), ('William', 'Taft'), ('Dwight', 'Eisenhower'), ('Charles', 'de Gaulle'), ('Helmut', 'Kohl'), ('Jacques', 'Chirac'), ('Nicolas', 'Sarkozy'), ('Francois', 'Hollande'), ('Sanna', 'Marin'), ('Pedro', 'Sanchez'), ('Andres', 'Obrador'), ('Luiz', 'Lula'), ('Dilma', 'Rousseff'), ('Michel', 'Temer'), ('Juan', 'Peron'), ('Eva', 'Peron'), ('Alberto', 'Fernandez'), ('Mauricio', 'Macri'), ('Sebastian', 'Pinera'), ('Michelle', 'Bachelet'), ('Jose', 'Mujica'), ('Tabare', 'Vazquez'), ('Carlos', 'Menem'), ('Alvaro', 'Uribe'), ('Ivan', 'Duque'), ('Felipe', 'Calderon'), ('Vicente', 'Fox'), ('Enrique', 'Nieto'), ('Alan', 'Garcia'), ('Ollanta', 'Humala'), ('Keiko', 'Fujimori'), ('Pedro', 'Castillo'), ('Alejandro', 'Toledo'), ('Abiy', 'Ahmed'), ('Hailemariam', 'Desalegn'), ('Jacob', 'Zuma'), ('Cyril', 'Ramaphosa'), ('Thabo', 'Mbeki'), ('Nelson', 'Mandela'), ('Paul', 'Kagame'), ('Yoweri', 'Museveni'), ('John', 'Magufuli'), ('Samia', 'Suluhu'), ('Uhuru', 'Kenyatta'), ('William', 'Ruto'), ('Ali', 'Bongo'), ('Paul', 'Biya'), ('Idriss', 'Deby'), ('Macky', 'Sall'), ('Muhammadu', 'Buhari'), ('Bola', 'Tinubu'), ('Goodluck', 'Jonathan'), ('Olusegun', 'Obasanjo'), ('Hosni', 'Mubarak'), ('Anwar', 'Sadat'), ('Gamal', 'Nasser'), ('Mohamed', 'Morsi'), ('Abdel', 'Sisi'), ('Bashar', 'Assad'), ('Saddam', 'Hussein'), ('Muammar', 'Gaddafi'), ('Recep', 'Erdogan'), ('Binali', 'Yildirim'), ('Ahmet', 'Davutoglu'), ('Tansu', 'Ciller'), ('Turgut', 'Ozal'), ('Suleyman', 'Demirel'), ('Ismet', 'Inonu'), ('Mustafa', 'Ataturk'), ('Benjamin', 'Netanyahu'), ('Yitzhak', 'Rabin'), ('Shimon', 'Peres'), ('Ariel', 'Sharon'), ('Ehud', 'Barak'), ('Ehud', 'Olmert'), ('Golda', 'Meir'), ('David', 'Ben-Gurion'), ('Menachem', 'Begin'), ('Itzhak', 'Shamir'), ('Yair', 'Lapid'), ('Naftali', 'Bennett'), ('Mahmoud', 'Abbas'), ('Yasser', 'Arafat'), ('King', 'Hussein'), ('King', 'Abdullah'), ('Hamad', 'bin Isa'), ('Salman', 'bin Abdulaziz'), ('Mohammed', 'bin Salman'), ('Tamim', 'bin Hamad'), ('Hassanal', 'Bolkiah'), ('Lee', 'Hsien Loong'), ('Mahathir', 'Mohamad'), ('Anwar', 'Ibrahim'), ('Joko', 'Widodo'), ('Susilo', 'Yudhoyono'), ('Abdurrahman', 'Wahid'), ('Megawati', 'Sukarnoputri'), ('Fumio', 'Kishida'), ('Yoshihide', 'Suga'), ('Shinzo', 'Abe'), ('Yukio', 'Hatoyama'), ('Taro', 'Aso'), ('Junichiro', 'Koizumi'), ('Keizo', 'Obuchi'), ('Ryutaro', 'Hashimoto'), ('Tomichi', 'Murayama'), ('Noboru', 'Takeshita'), ('Takeo', 'Fukuda'), ('Yasuhiro', 'Nakasone'), ('Yoshida', 'Shigeru'), ('Ichiro', 'Hatoyama'), ('Takashi', 'Hara'), ('Hitoshi', 'Ashida'), ('Morihiro', 'Hosokawa'), ('Hideki', 'Tojo'), ('Toshiki', 'Kaifu'), ('Shigeru', 'Ishiba'), ('Ban', 'Ki-moon'), ('Syngman', 'Rhee'), ('Kim', 'Dae-jung'), ('Kim', 'Young-sam'), ('Moon', 'Jae-in'), ('Park', 'Geun-hye'), ('Park', 'Chung-hee'), ('Chun', 'Doo-hwan'), ('Roh', 'Tae-woo'), ('Roh', 'Moo-hyun'), ('Yoon', 'Suk-yeol'), ('Lee', 'Myung-bak'), ('Carlos', 'Alvarado'), ('Laura', 'Chinchilla'), ('Oscar', 'Arias'), ('Daniel', 'Ortega'), ('Violeta', 'Chamorro'), ('Rafael', 'Correa'), ('Guillermo', 'Lasso'), ('Lenin', 'Moreno'), ('Evo', 'Morales'), ('Jeanine', 'Anez'), ('Luis', 'Arce'), ('Sebastian', 'Kurz'), ('Karl', 'Nehammer'), ('Alexander', 'Schallenberg'), ('Brigitte', 'Bierlein'), ('Werner', 'Faymann'), ('Alfred', 'Gusenbauer'), ('Wolfgang', 'Schuessel'), ('Viktor', 'Orban'), ('Katalin', 'Novak'), ('Mateusz', 'Morawiecki'), ('Andrzej', 'Duda'), ('Jaroslaw', 'Kaczynski'), ('Lech', 'Walesa'), ('Donald', 'Tusk'), ('Bronislaw', 'Komorowski'), ('Aleksandar', 'Vucic'), ('Slobodan', 'Milosevic'), ('Zoran', 'Djindjic'), ('Milo', 'Djukanovic'), ('Boris', 'Tadic'), ('Ivan', 'Gasparovic'), ('Robert', 'Fico'), ('Zuzana', 'Caputova'), ('Milos', 'Zeman'), ('Petr', 'Fiala'), ('Vaclav', 'Klaus'), ('Vaclav', 'Havel'), ('Jan', 'Fischer'), ('Bohuslav', 'Sobotka')]
        coach_names = [("Winston", "Churchill"), ("Margaret", "Thatcher"), ("Jean", "Chrétien"), ("Stephen", "Harper")]
        coordinator_names = [("Theodore", "Roosevelt"), ("Lester", "Pearson"), ("Nelson", "Mandela"), ("Jacinda", "Ardern")]

        player_counter = 0
        player_name_index = 0
        all_divisions = []

        league_objs = {}
        for name in league_names:
            league_objs[name], _ = League.objects.get_or_create(name=name)

        for league_name in league_names:
            league = league_objs[league_name]
            for d in range(1, divisions_per_league + 1):
                division_name = f"{league_name} - Division {d}"
                division, _ = Division.objects.get_or_create(name=division_name, league=league)
                all_divisions.append(division)

                teams = []
                for t in range(1, teams_per_division + 1):
                    team_name = f"{division_name} Team {t}"
                    team, _ = Team.objects.get_or_create(name=team_name, division=division)
                    teams.append(team)

                for team_index, team in enumerate(teams):
                    for _ in range(10):  # 10 players per team
                        if player_name_index >= len(player_names):
                            break
                        fn, ln = player_names[player_name_index]
                        clean_ln = ln.lower().replace(" ", "").replace("'", "")
                        username = f"{fn.lower()}{clean_ln}"
                        user = User.objects.create_user(username=username, password="test1234", email=f"{username}@test.com")
                        player = Player.objects.create(user=user, first_name=fn, last_name=ln, division=division)
                        player.teams.add(team)
                        player_name_index += 1

        superuser, created = User.objects.get_or_create(username="eugenelin89", defaults={
            "email": "eugene@example.com", "is_superuser": True, "is_staff": True
        })
        if created:
            superuser.set_password("mounties")
            superuser.save()

        for division in all_divisions:
            division.coordinators.add(superuser)

        for i, (fn, ln) in enumerate(coordinator_names):
            username = f"coord{i+1}"
            user = User.objects.create_user(username=username.lower(), password="test1234", email=f"{username}@test.com")
            for div in all_divisions[i::len(coordinator_names)]:
                div.coordinators.add(user)

        teams = Team.objects.all()
        for i, team in enumerate(teams):
            fn, ln = coach_names[i % len(coach_names)]
            username = f"coach{i+1}"
            user = User.objects.create_user(username=username.lower(), password="test1234", email=f"{username}@test.com")
            team.coaches.add(user)

        self.stdout.write(self.style.SUCCESS("✅ Seeded deterministic test data with politician names."))

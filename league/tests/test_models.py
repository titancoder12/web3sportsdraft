from django.test import TestCase
from django.contrib.auth.models import User
from league.models import League, Division, Team, Player, Game, PlayerGameStat, FairPlayRuleSet, LineupPlan, LineupEntry, LineupCompliance
from datetime import datetime, time

class LeagueModelTests(TestCase):
    def setUp(self):
        self.league = League.objects.create(
            name="Test League",
            description="Test Description"
        )

    def test_league_creation(self):
        self.assertEqual(self.league.name, "Test League")
        self.assertEqual(self.league.description, "Test Description")
        self.assertEqual(str(self.league), "Test League")

class DivisionModelTests(TestCase):
    def setUp(self):
        self.league = League.objects.create(name="Test League")
        self.division = Division.objects.create(
            name="11U",
            league=self.league,
            is_open=True
        )
        self.user = User.objects.create_user(username="testcoach", password="testpass")

    def test_division_creation(self):
        self.assertEqual(self.division.name, "11U")
        self.assertEqual(self.division.league, self.league)
        self.assertTrue(self.division.is_open)
        self.assertEqual(str(self.division), "Test League - 11U")

    def test_division_coordinators(self):
        self.division.coordinators.add(self.user)
        self.assertTrue(self.division.coordinators.filter(id=self.user.id).exists())

class TeamModelTests(TestCase):
    def setUp(self):
        self.league = League.objects.create(name="Test League")
        self.division = Division.objects.create(
            name="11U",
            league=self.league
        )
        self.team = Team.objects.create(
            name="Test Team",
            division=self.division,
            max_players=12
        )
        self.coach = User.objects.create_user(username="testcoach", password="testpass")

    def test_team_creation(self):
        self.assertEqual(self.team.name, "Test Team")
        self.assertEqual(self.team.division, self.division)
        self.assertEqual(self.team.max_players, 12)
        self.assertEqual(str(self.team), "Test Team")

    def test_team_coaches(self):
        self.team.coaches.add(self.coach)
        self.assertTrue(self.team.coaches.filter(id=self.coach.id).exists())

class PlayerModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testplayer",
            password="testpass",
            first_name="Test",
            last_name="Player"
        )
        self.league = League.objects.create(name="Test League")
        self.division = Division.objects.create(
            name="11U",
            league=self.league
        )
        self.team = Team.objects.create(
            name="Test Team",
            division=self.division
        )
        self.player = Player.objects.create(
            user=self.user,
            first_name="Test",
            last_name="Player",
            division=self.division
        )
        self.player.teams.add(self.team)

    def test_player_creation(self):
        """Test player creation and string representation"""
        self.assertEqual(str(self.player), "Test Player")

    def test_player_teams(self):
        self.assertTrue(self.player.teams.filter(id=self.team.id).exists())

class GameModelTests(TestCase):
    def setUp(self):
        self.league = League.objects.create(name="Test League")
        self.division = Division.objects.create(
            name="11U",
            league=self.league
        )
        self.team1 = Team.objects.create(
            name="Team 1",
            division=self.division
        )
        self.team2 = Team.objects.create(
            name="Team 2",
            division=self.division
        )
        self.game = Game.objects.create(
            game_id="TEST123",
            team_home=self.team1,
            team_away=self.team2,
            date=datetime.now(),
            time=time(14, 0),
            location="Test Field"
        )

    def test_game_creation(self):
        self.assertEqual(self.game.game_id, "TEST123")
        self.assertEqual(self.game.team_home, self.team1)
        self.assertEqual(self.game.team_away, self.team2)
        self.assertFalse(self.game.finalized)
        self.assertFalse(self.game.is_verified)

class FairPlayRuleSetTests(TestCase):
    def setUp(self):
        self.league = League.objects.create(name="Test League")
        self.rules = FairPlayRuleSet.objects.create(
            league=self.league,
            age_group="11U",
            min_innings_per_player=3,
            max_consecutive_bench_innings=1,
            min_plate_appearances=2,
            enforce_plate_appearance=True,
            enforce_position_rotation=True,
            max_innings_per_position={"C": 3, "P": 3}
        )

    def test_rules_creation(self):
        self.assertEqual(self.rules.age_group, "11U")
        self.assertEqual(self.rules.min_innings_per_player, 3)
        self.assertEqual(self.rules.max_consecutive_bench_innings, 1)
        self.assertTrue(self.rules.enforce_plate_appearance)
        self.assertTrue(self.rules.enforce_position_rotation)
        self.assertEqual(self.rules.max_innings_per_position, {"C": 3, "P": 3})

class LineupTests(TestCase):
    def setUp(self):
        self.league = League.objects.create(name="Test League")
        self.division = Division.objects.create(
            name="11U",
            league=self.league
        )
        self.team = Team.objects.create(
            name="Test Team",
            division=self.division
        )
        self.coach = User.objects.create_user(username="testcoach", password="testpass")
        self.team.coaches.add(self.coach)
        
        self.lineup_plan = LineupPlan.objects.create(
            team=self.team,
            coach=self.coach,
            notes="Test lineup"
        )
        
        self.player = Player.objects.create(
            first_name="Test",
            last_name="Player",
            division=self.division
        )
        self.player.teams.add(self.team)

    def test_lineup_creation(self):
        entry = LineupEntry.objects.create(
            lineup_plan=self.lineup_plan,
            player=self.player,
            batting_order=1,
            positions_by_inning={"1": "C", "2": "P", "3": "1B"}
        )
        
        self.assertEqual(entry.batting_order, 1)
        self.assertEqual(entry.positions_by_inning, {"1": "C", "2": "P", "3": "1B"})
        
        compliance = LineupCompliance.objects.create(
            lineup_plan=self.lineup_plan,
            player=self.player,
            innings_played=3,
            consecutive_bench_innings=0,
            plate_appearances=2,
            is_compliant=True
        )
        
        self.assertEqual(compliance.innings_played, 3)
        self.assertTrue(compliance.is_compliant) 
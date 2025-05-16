from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from league.models import League, Division, Team, Player, Game, PlayerGameStat, FairPlayRuleSet, LineupPlan
from datetime import datetime, time
from django.utils import timezone

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass",
            is_staff=True
        )
        self.client.login(username="testuser", password="testpass")
        
        self.league = League.objects.create(name="Test League")
        self.league.coordinators.add(self.user)  # Make user a coordinator
        
        self.division = Division.objects.create(
            name="11U",
            league=self.league
        )
        self.team = Team.objects.create(
            name="Test Team",
            division=self.division
        )
        self.team.coaches.add(self.user)
        
        self.player = Player.objects.create(
            first_name="Test",
            last_name="Player",
            division=self.division,
            user=self.user
        )
        self.player.teams.add(self.team)

    def test_dashboard_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirects to appropriate dashboard
        self.assertRedirects(response, reverse('player_dashboard'))

    def test_dashboard_with_division_view(self):
        response = self.client.get(reverse('dashboard_with_division', args=[self.division.id]))
        self.assertEqual(response.status_code, 302)  # Redirects to appropriate dashboard
        self.assertRedirects(response, reverse('player_dashboard'))

    def test_player_detail_view(self):
        response = self.client.get(reverse('player_detail', args=[self.player.id]))
        self.assertEqual(response.status_code, 200)

    def test_player_profile_view(self):
        """Test player profile view"""
        self.client.force_login(self.user)  # Force login to ensure authentication
        response = self.client.get(reverse('player_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'league/player_profile.html')
        self.assertContains(response, "Test Player")

class FairPlayTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testcoach",
            password="testpass"
        )
        self.client.login(username="testcoach", password="testpass")
        
        self.league = League.objects.create(name="Test League")
        self.league.coordinators.add(self.user)  # Make user a coordinator
        
        self.division = Division.objects.create(
            name="11U",
            league=self.league
        )
        self.team = Team.objects.create(
            name="Test Team",
            division=self.division
        )
        self.team.coaches.add(self.user)
        
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
        
        self.lineup_plan = LineupPlan.objects.create(
            team=self.team,
            coach=self.user,
            notes="Test lineup"
        )

    def test_fair_play_rules_view(self):
        response = self.client.get(reverse('fair_play_rules', args=[self.league.id]))
        self.assertEqual(response.status_code, 200)

    def test_check_lineup_compliance_view(self):
        response = self.client.get(reverse('check_lineup_compliance', args=[self.lineup_plan.id]))
        self.assertEqual(response.status_code, 302)  # Redirects after checking

class GameTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testcoach",
            password="testpass"
        )
        self.client.login(username="testcoach", password="testpass")
        
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
        self.team1.coaches.add(self.user)
        
        self.game = Game.objects.create(
            game_id="TEST123",
            team_home=self.team1,
            team_away=self.team2,
            date=timezone.now(),
            time=time(14, 0),
            location="Test Field"
        )

    def test_box_score_view(self):
        """Test box score view"""
        response = self.client.get(reverse('box_score', kwargs={'game_id': self.game.game_id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'league/box_score.html')
        self.assertContains(response, self.team1.name)
        self.assertContains(response, self.team2.name)

    def test_review_stats_view(self):
        response = self.client.get(reverse('review_stats'))
        self.assertEqual(response.status_code, 200)

class TeamTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testcoach",
            password="testpass"
        )
        self.client.login(username="testcoach", password="testpass")
        
        self.league = League.objects.create(name="Test League")
        self.division = Division.objects.create(
            name="11U",
            league=self.league
        )
        self.team = Team.objects.create(
            name="Test Team",
            division=self.division
        )
        self.team.coaches.add(self.user)

    def test_coach_dashboard_view(self):
        response = self.client.get(reverse('coach_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_team_logs_view(self):
        response = self.client.get(reverse('team_logs', args=[self.team.id]))
        self.assertEqual(response.status_code, 200) 
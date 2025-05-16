from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from league.models import League, Division, Team, Player, Game, PlayerGameStat, FairPlayRuleSet, LineupPlan
from datetime import datetime, time
from django.utils import timezone
import json

class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass",
            is_staff=True
        )
        self.client.force_authenticate(user=self.user)
        
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
            first_name="Test",
            last_name="Player",
            division=self.division
        )
        self.player.teams.add(self.team)

    def test_league_list(self):
        url = reverse('league-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_league_detail(self):
        url = reverse('league-detail', args=[self.league.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test League")

    def test_division_list(self):
        url = reverse('division-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_team_list(self):
        url = reverse('team-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_player_list(self):
        url = reverse('player-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class GameAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testcoach",
            password="testpass"
        )
        self.client.force_authenticate(user=self.user)
        
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

    def test_game_list(self):
        url = reverse('game-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_game_detail(self):
        """Test retrieving a game"""
        response = self.client.get(reverse('game-detail', args=[self.game.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['game_id'], self.game.game_id)

    def test_game_create(self):
        """Test creating a game"""
        data = {
            'game_id': 'TEST456',
            'team_home': reverse('team-detail', args=[self.team1.id]),
            'team_away': reverse('team-detail', args=[self.team2.id]),
            'date': timezone.now().isoformat(),
            'time': '14:00:00',
            'location': 'Test Field'
        }
        response = self.client.post(reverse('game-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Game.objects.count(), 2)
        self.assertEqual(Game.objects.get(game_id='TEST456').game_id, 'TEST456')

class FairPlayAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testcoach",
            password="testpass"
        )
        self.client.force_authenticate(user=self.user)
        
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

    def test_rules_list(self):
        url = reverse('fairplayruleset-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_rules_detail(self):
        url = reverse('fairplayruleset-detail', args=[self.rules.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['age_group'], "11U")

    def test_lineup_plan_list(self):
        url = reverse('lineupplan-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_lineup_plan_detail(self):
        url = reverse('lineupplan-detail', args=[self.lineup_plan.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['notes'], "Test lineup")

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass"
        )
        self.league = League.objects.create(name="Test League")

    def test_unauthorized_access(self):
        url = reverse('league-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authorized_access(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('league-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_staff_only_access(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('league-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK) 
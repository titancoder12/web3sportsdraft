from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from league.models import (
    League, Division, Team, Player, Game, PlayerGameStat,
    FairPlayRuleSet, LineupPlan, LineupEntry, LineupCompliance
)
from datetime import datetime, time
from django.utils import timezone
import json

class GameWorkflowTests(TestCase):
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
        
        self.player1 = Player.objects.create(
            first_name="Player",
            last_name="One",
            division=self.division
        )
        self.player2 = Player.objects.create(
            first_name="Player",
            last_name="Two",
            division=self.division
        )
        self.player1.teams.add(self.team1)
        self.player2.teams.add(self.team1)
        
        self.game = Game.objects.create(
            game_id="TEST123",
            team_home=self.team1,
            team_away=self.team2,
            date=timezone.now().date(),
            time=time(14, 0),
            location="Test Field"
        )

    def test_complete_game_workflow(self):
        # Create game
        response = self.client.post(
            reverse('create_game', args=[self.team1.id]),
            {
                'team_away': self.team2.id,
                'date': timezone.now().date(),
                'time': time(14, 0),
                'location': 'Test Field'
            }
        )
        self.assertEqual(response.status_code, 200)  # Returns to form page
        
        # Verify game creation
        game = Game.objects.get(team_home=self.team1, team_away=self.team2)
        self.assertEqual(game.location, 'Test Field')
        
        # Record stats
        response = self.client.post(
            reverse('record_stats', args=[game.game_id]),
            {
                'player': self.player1.id,
                'at_bats': 3,
                'hits': 2,
                'runs': 1,
                'rbis': 1
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirects after recording stats
        
        # Verify stats
        stats = PlayerGameStat.objects.filter(game=game, player=self.player1)
        self.assertEqual(stats.count(), 1)
        self.assertEqual(stats.first().hits, 2)

class FairPlayWorkflowTests(TestCase):
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
        
        self.player1 = Player.objects.create(
            first_name="Test",
            last_name="Player1",
            division=self.division
        )
        self.player2 = Player.objects.create(
            first_name="Test",
            last_name="Player2",
            division=self.division
        )
        self.player1.teams.add(self.team)
        self.player2.teams.add(self.team)
        
        self.rules = FairPlayRuleSet.objects.create(
            league=self.league,
            age_group="11U",
            min_innings_per_player=3,
            max_consecutive_bench_innings=1,
            min_plate_appearances=2,
            enforce_plate_appearance=True,
            enforce_position_rotation=True,
            max_innings_per_position={"C": 3, "P": 3, "1B": 3}
        )
        
        self.lineup_plan = LineupPlan.objects.create(
            team=self.team,
            coach=self.user,
            notes="Test lineup"
        )

    def test_complete_fairplay_workflow(self):
        # Create lineup entry
        response = self.client.post(
            reverse('lineup_entries', args=[self.lineup_plan.id]),
            {
                'player': self.player1.id,
                'batting_order': 1,
                'positions_by_inning': '{"1": "P", "2": "C", "3": "1B"}'
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirects after adding entry
        
        # Create a second entry to test compliance
        response = self.client.post(
            reverse('lineup_entries', args=[self.lineup_plan.id]),
            {
                'player': self.player2.id,
                'batting_order': 2,
                'positions_by_inning': '{"1": "C", "2": "P", "3": "1B"}'
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirects after adding entry
        
        # Check compliance
        response = self.client.post(
            reverse('check_lineup_compliance', args=[self.lineup_plan.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirects after checking
        
        # Verify compliance results
        compliance = LineupCompliance.objects.filter(lineup_plan=self.lineup_plan)
        self.assertEqual(compliance.count(), 2)
        
        # Print compliance details for debugging
        for c in compliance:
            print(f"\nPlayer: {c.player.first_name} {c.player.last_name}")
            print(f"Is compliant: {c.is_compliant}")
            print(f"Violations: {c.violation_details}")
            print(f"Innings played: {c.innings_played}")
            print(f"Position violations: {c.position_violations}")
            print(f"Plate appearances: {c.plate_appearances}")
        
        self.assertTrue(all(c.is_compliant for c in compliance))

class PlayerRegistrationWorkflowTests(TestCase):
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

    def test_complete_registration_workflow(self):
        # Register player
        response = self.client.post(
            reverse('register_player'),
            {
                'first_name': 'Test',
                'last_name': 'Player',
                'division': self.division.id,
                'age': 11,
                'parent_name': 'Parent Name',
                'parent_email': 'parent@test.com',
                'parent_phone': '123-456-7890',
                'user': self.user.id,
                'teams': [self.team.id]
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify player creation
        player = Player.objects.get(first_name='Test', last_name='Player')
        self.assertEqual(player.division, self.division)
        self.assertEqual(player.teams.first(), self.team)
        self.assertEqual(player.parent_phone, '123-456-7890')
        
        # Check player profile
        response = self.client.get(reverse('player_profile'))
        self.assertEqual(response.status_code, 200)
        
        # Update player information
        update_data = {
            'first_name': 'Test',
            'last_name': 'Player',
            'parent_name': 'Parent Name',
            'parent_email': 'parent@test.com',
            'parent_phone': '987-654-3210',
            'user': self.user.id,
            'teams': [self.team.id],
            'division': self.division.id
        }
        response = self.client.post(
            reverse('update_player', args=[player.id]),
            update_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify update
        player.refresh_from_db()
        self.assertEqual(player.parent_phone, '987-654-3210') 
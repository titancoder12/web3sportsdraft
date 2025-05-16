from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from league.models import (
    League, Division, Team, Player, Game, PlayerGameStat,
    FairPlayRuleSet, LineupPlan, LineupEntry, LineupCompliance
)
from datetime import datetime, time
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
            date=datetime.now(),
            time=time(14, 0),
            location="Test Field"
        )

    def test_complete_game_workflow(self):
        # 1. Create lineup plan
        lineup_data = {
            'team': self.team1.id,
            'notes': 'Test lineup'
        }
        response = self.client.post(reverse('create_lineup'), lineup_data)
        self.assertEqual(response.status_code, 302)
        lineup_plan = LineupPlan.objects.latest('id')
        
        # 2. Add lineup entries
        entry_data = {
            'player': self.player1.id,
            'batting_order': 1,
            'positions_by_inning': json.dumps({"1": "C", "2": "P", "3": "1B"})
        }
        response = self.client.post(
            reverse('add_lineup_entry', args=[lineup_plan.id]),
            entry_data
        )
        self.assertEqual(response.status_code, 302)
        
        # 3. Record game stats
        stat_data = {
            'player': self.player1.id,
            'game': self.game.id,
            'at_bats': 3,
            'hits': 2,
            'runs': 1,
            'rbis': 1
        }
        response = self.client.post(
            reverse('record_stats', args=[self.game.game_id]),
            stat_data
        )
        self.assertEqual(response.status_code, 302)
        
        # 4. Verify stats
        stat = PlayerGameStat.objects.latest('id')
        response = self.client.post(
            reverse('verify_stat', args=[stat.id])
        )
        self.assertEqual(response.status_code, 302)
        
        # 5. Finalize game
        response = self.client.post(
            reverse('finalize_game', args=[self.game.game_id])
        )
        self.assertEqual(response.status_code, 302)
        
        # Verify final state
        self.game.refresh_from_db()
        self.assertTrue(self.game.finalized)
        self.assertTrue(self.game.is_verified)

class FairPlayWorkflowTests(TestCase):
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
        
        self.players = []
        for i in range(12):
            player = Player.objects.create(
                first_name=f"Player{i}",
                last_name=f"Test{i}",
                division=self.division
            )
            player.teams.add(self.team)
            self.players.append(player)

    def test_complete_fairplay_workflow(self):
        # 1. Create lineup plan
        lineup_data = {
            'team': self.team.id,
            'notes': 'Fair play test lineup'
        }
        response = self.client.post(reverse('create_lineup'), lineup_data)
        self.assertEqual(response.status_code, 302)
        lineup_plan = LineupPlan.objects.latest('id')
        
        # 2. Add lineup entries for all players
        for i, player in enumerate(self.players, 1):
            entry_data = {
                'player': player.id,
                'batting_order': i,
                'positions_by_inning': json.dumps({
                    "1": "C" if i <= 3 else "OF",
                    "2": "P" if i <= 3 else "IF",
                    "3": "1B" if i <= 3 else "OF"
                })
            }
            response = self.client.post(
                reverse('add_lineup_entry', args=[lineup_plan.id]),
                entry_data
            )
            self.assertEqual(response.status_code, 302)
        
        # 3. Check compliance
        response = self.client.get(
            reverse('check_lineup_compliance', args=[lineup_plan.id])
        )
        self.assertEqual(response.status_code, 302)
        
        # 4. Verify compliance results
        compliance = LineupCompliance.objects.filter(lineup_plan=lineup_plan)
        self.assertEqual(compliance.count(), len(self.players))
        self.assertTrue(all(c.is_compliant for c in compliance))

class PlayerRegistrationWorkflowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testparent",
            password="testpass"
        )
        self.client.login(username="testparent", password="testpass")
        
        self.league = League.objects.create(name="Test League")
        self.division = Division.objects.create(
            name="11U",
            league=self.league,
            is_open=True
        )

    def test_complete_registration_workflow(self):
        # 1. Register player
        player_data = {
            'first_name': 'Test',
            'last_name': 'Player',
            'division': self.division.id,
            'birth_date': '2012-01-01',
            'parent_name': 'Parent Name',
            'parent_email': 'parent@test.com',
            'parent_phone': '123-456-7890'
        }
        response = self.client.post(reverse('register_player'), player_data)
        self.assertEqual(response.status_code, 302)
        
        # 2. Verify player creation
        player = Player.objects.get(first_name='Test', last_name='Player')
        self.assertEqual(player.division, self.division)
        
        # 3. Check player profile
        response = self.client.get(reverse('player_profile'))
        self.assertEqual(response.status_code, 200)
        
        # 4. Update player information
        update_data = {
            'first_name': 'Test',
            'last_name': 'Player',
            'parent_phone': '987-654-3210'
        }
        response = self.client.post(
            reverse('update_player', args=[player.id]),
            update_data
        )
        self.assertEqual(response.status_code, 302)
        
        # 5. Verify update
        player.refresh_from_db()
        self.assertEqual(player.parent_phone, '987-654-3210') 
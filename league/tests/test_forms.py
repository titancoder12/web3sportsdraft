from django.test import TestCase
from django.contrib.auth.models import User
from league.models import League, Division, Team, Player, Game, FairPlayRuleSet, LineupPlan
from league.forms import (
    LeagueForm, DivisionForm, TeamForm, PlayerForm, GameForm,
    FairPlayRuleSetForm, LineupPlanForm, LineupEntryForm
)
from datetime import datetime, time
import json

class LeagueFormTests(TestCase):
    def setUp(self):
        self.form_data = {
            'name': 'Test League',
            'description': 'Test Description'
        }

    def test_league_form_valid(self):
        form = LeagueForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_league_form_invalid(self):
        form_data = self.form_data.copy()
        form_data['name'] = ''  # Required field
        form = LeagueForm(data=form_data)
        self.assertFalse(form.is_valid())

class DivisionFormTests(TestCase):
    def setUp(self):
        self.league = League.objects.create(name="Test League")
        self.form_data = {
            'name': '11U',
            'league': self.league.id,
            'is_open': True
        }

    def test_division_form_valid(self):
        form = DivisionForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_division_form_invalid(self):
        form_data = self.form_data.copy()
        form_data['name'] = ''  # Required field
        form = DivisionForm(data=form_data)
        self.assertFalse(form.is_valid())

class TeamFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testcoach', password='testpass')
        self.league = League.objects.create(name='Test League')
        self.division = Division.objects.create(name='11U', league=self.league)
        self.form_data = {
            'name': 'Test Team',
            'division': self.division.id,
            'max_players': 12,
            'coaches': [self.user.id]
        }

    def test_team_form_valid(self):
        form = TeamForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_team_form_invalid(self):
        form_data = self.form_data.copy()
        form_data['name'] = ''  # Required field
        form = TeamForm(data=form_data)
        self.assertFalse(form.is_valid())

class PlayerFormTests(TestCase):
    def setUp(self):
        self.league = League.objects.create(name="Test League")
        self.division = Division.objects.create(
            name="11U",
            league=self.league
        )
        self.form_data = {
            'first_name': 'Test',
            'last_name': 'Player',
            'division': self.division.id
        }

    def test_player_form_valid(self):
        form = PlayerForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_player_form_invalid(self):
        form_data = self.form_data.copy()
        form_data['first_name'] = ''  # Required field
        form = PlayerForm(data=form_data)
        self.assertFalse(form.is_valid())

class GameFormTests(TestCase):
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
        self.form_data = {
            'game_id': 'TEST123',
            'team_home': self.team1.id,
            'team_away': self.team2.id,
            'date': datetime.now().date(),
            'time': time(14, 0),
            'location': 'Test Field'
        }

    def test_game_form_valid(self):
        form = GameForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_game_form_invalid(self):
        form_data = self.form_data.copy()
        form_data['game_id'] = ''  # Required field
        form = GameForm(data=form_data)
        self.assertFalse(form.is_valid())

class FairPlayRuleSetFormTests(TestCase):
    def setUp(self):
        self.league = League.objects.create(name="Test League")
        self.form_data = {
            'league': self.league.id,
            'age_group': '11U',
            'min_innings_per_player': 3,
            'max_consecutive_bench_innings': 1,
            'min_plate_appearances': 2,
            'enforce_plate_appearance': True,
            'enforce_position_rotation': True,
            'max_innings_per_position': '{"C": 3, "P": 3}'
        }

    def test_rules_form_valid(self):
        form = FairPlayRuleSetForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_rules_form_invalid(self):
        form_data = self.form_data.copy()
        form_data['age_group'] = ''  # Required field
        form = FairPlayRuleSetForm(data=form_data)
        self.assertFalse(form.is_valid())

class LineupFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testcoach', password='testpass')
        self.league = League.objects.create(name='Test League')
        self.division = Division.objects.create(name='11U', league=self.league)
        self.team = Team.objects.create(name='Test Team', division=self.division)
        self.team.coaches.add(self.user)
        self.player = Player.objects.create(
            first_name='Test',
            last_name='Player',
            division=self.division,
            user=self.user
        )
        self.player.teams.add(self.team)

    def test_lineup_plan_form_valid(self):
        form_data = {
            'team': self.team.id,
            'coach': self.user.id,
            'notes': 'Test lineup notes'
        }
        form = LineupPlanForm(data=form_data, team=self.team)
        self.assertTrue(form.is_valid())

    def test_lineup_entry_form_valid(self):
        form_data = {
            'player': self.player.id,
            'batting_order': 1,
            'positions_by_inning': '{"1": "P", "2": "C", "3": "1B"}'
        }
        form = LineupEntryForm(data=form_data, team=self.team)
        if not form.is_valid():
            print("Form errors:", form.errors)
        self.assertTrue(form.is_valid(), form.errors.as_text())

    def test_lineup_entry_form_invalid(self):
        form_data = {
            'player': self.player.id,
            'batting_order': 0,  # Invalid batting order
            'positions_by_inning': '{"1": "C", "2": "P", "3": "1B"}'
        }
        form = LineupEntryForm(data=form_data, team=self.team)
        self.assertFalse(form.is_valid()) 
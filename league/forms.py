# league/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Player, Division, Team, JoinTeamRequest, PlayerGameStat, FairPlayRuleSet, LineupPlan, LineupEntry, Game
from django.db.models import Q
from django.utils import timezone

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['first_name', 'last_name', 'age', 'position', 'rating', 'division']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 5, 'max': 18}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'division': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['age'].required = False
        self.fields['position'].required = False
        self.fields['rating'].required = False
        self.fields['division'].required = True

class PlayerProfileForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['first_name', 'last_name', 'age', 'position', 'description']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 5, 'max': 18}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['age'].required = False
        self.fields['position'].required = False
        self.fields['description'].required = False

class CoachCommentForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['coach_comments']
        widgets = {
            'coach_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class PlayerSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.username = self.cleaned_data['username']
        if commit:
            user.save()
            Player.objects.create(
                user=user,
                first_name=user.first_name,
                last_name=user.last_name,
            )
        return user

class PlayerCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="Upload CSV File", widget=forms.FileInput(attrs={'class': 'form-control'}))
    division = forms.ModelChoiceField(
        queryset=Division.objects.all(),
        label="Select Division",
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="-- Select a Division --"
    )

class JoinTeamRequestForm(forms.ModelForm):
    class Meta:
        model = JoinTeamRequest
        fields = ['team']
        widgets = {
            'team': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        player = kwargs.pop('player', None)
        super().__init__(*args, **kwargs)
        if player:
            # Optional: Only show teams the player isn't already on or hasn't already requested
            existing_team_ids = player.teams.values_list('id', flat=True)
            requested_team_ids = JoinTeamRequest.objects.filter(player=player).values_list('team_id', flat=True)
            self.fields['team'].queryset = Team.objects.exclude(id__in=existing_team_ids.union(requested_team_ids))

class PlayerGameStatForm(forms.ModelForm):
    class Meta:
        model = PlayerGameStat
        fields = [
            'game', 
            'at_bats',
            'hits',
            'runs',
            'rbis',
            'home_runs',
            'singles',
            'doubles',
            'triples',
            'strikeouts',
            'base_on_balls',
            'hit_by_pitch',
            'sacrifice_flies',
            'innings_pitched',
            'hits_allowed', 
            'runs_allowed',
            'earned_runs',
            'walks_allowed',
            'strikeouts_pitching',
            'home_runs_allowed',
        ]
        widgets = {
            'game': forms.Select(attrs={'class': 'form-select'}),
            'at_bats': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'hits': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'runs': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'rbis': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'home_runs': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'singles': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'doubles': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'triples': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'strikeouts': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'base_on_balls': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'hit_by_pitch': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'sacrifice_flies': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'innings_pitched': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 0.1}),
            'hits_allowed': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'runs_allowed': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'earned_runs': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'walks_allowed': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'strikeouts_pitching': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'home_runs_allowed': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

class FairPlayRuleSetForm(forms.ModelForm):
    class Meta:
        model = FairPlayRuleSet
        fields = [
            'league', 'age_group', 'min_innings_per_player',
            'max_consecutive_bench_innings', 'min_plate_appearances',
            'enforce_plate_appearance', 'enforce_position_rotation',
            'max_innings_per_position', 'eh_option_start_date',
            'eh_option_end_date', 'no_mandated_fair_play'
        ]
        widgets = {
            'league': forms.Select(attrs={'class': 'form-select'}),
            'age_group': forms.TextInput(attrs={'class': 'form-control'}),
            'min_innings_per_player': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'max_consecutive_bench_innings': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'min_plate_appearances': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'enforce_plate_appearance': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'enforce_position_rotation': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'max_innings_per_position': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'eh_option_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'eh_option_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'no_mandated_fair_play': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# class PlayerAvailabilityForm(forms.ModelForm):
#     class Meta:
#         model = PlayerAvailability
#         fields = ['status', 'notes']
#         widgets = {
#             'status': forms.Select(attrs={'class': 'form-select'}),
#             'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
#         }

class LineupPlanForm(forms.ModelForm):
    class Meta:
        model = LineupPlan
        fields = ['game', 'notes']
        widgets = {
            'game': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team', None)
        super().__init__(*args, **kwargs)
        if team:
            self.fields['game'].queryset = Game.objects.filter(
                Q(team_home=team) | Q(team_away=team)
            ).filter(date__gte=timezone.now())

class LineupEntryForm(forms.ModelForm):
    class Meta:
        model = LineupEntry
        fields = ['player', 'batting_order', 'positions_by_inning']
        widgets = {
            'player': forms.Select(attrs={'class': 'form-select'}),
            'batting_order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'positions_by_inning': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team', None)
        super().__init__(*args, **kwargs)
        if team:
            self.fields['player'].queryset = team.players.all()

class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['team_away', 'date', 'time', 'location']
        widgets = {
            'team_away': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        team_home = kwargs.pop('team_home', None)
        super().__init__(*args, **kwargs)
        if team_home:
            # Only show teams from the same division
            self.fields['team_away'].queryset = Team.objects.filter(
                division=team_home.division
            ).exclude(id=team_home.id)


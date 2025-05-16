# league/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Player, Division, Team, JoinTeamRequest, PlayerGameStat, FairPlayRuleSet, LineupPlan, LineupEntry, Game, League
from django.db.models import Q
from django.utils import timezone
import json

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['first_name', 'last_name', 'age', 'position', 'rating', 'division', 'teams', 'user', 'parent_name', 'parent_email', 'parent_phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 5, 'max': 18}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'division': forms.Select(attrs={'class': 'form-control'}),
            'teams': forms.SelectMultiple(attrs={'class': 'select2'}),
            'parent_name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'parent_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['age'].required = False
        self.fields['position'].required = False
        self.fields['rating'].required = False
        self.fields['division'].required = True
        self.fields['parent_name'].required = False
        self.fields['parent_email'].required = False
        self.fields['parent_phone'].required = False

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
        fields = ['player', 'at_bats', 'hits', 'runs', 'rbis']
        widgets = {
            'player': forms.Select(attrs={'class': 'form-control'}),
            'at_bats': forms.NumberInput(attrs={'class': 'form-control'}),
            'hits': forms.NumberInput(attrs={'class': 'form-control'}),
            'runs': forms.NumberInput(attrs={'class': 'form-control'}),
            'rbis': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class FairPlayRuleSetForm(forms.ModelForm):
    class Meta:
        model = FairPlayRuleSet
        fields = ['league', 'age_group', 'min_innings_per_player', 'max_consecutive_bench_innings', 'min_plate_appearances', 'enforce_plate_appearance', 'enforce_position_rotation', 'max_innings_per_position']
        widgets = {
            'max_innings_per_position': forms.Textarea(attrs={'rows': 4}),
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
        fields = ['team', 'coach', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
            'coach': forms.HiddenInput(),
            'team': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team', None)
        super().__init__(*args, **kwargs)
        if team:
            self.fields['team'].initial = team
            self.fields['coach'].initial = team.coaches.first()
            self.fields['team'].required = True
            self.fields['coach'].required = True

    def clean(self):
        cleaned_data = super().clean()
        team = cleaned_data.get('team')
        coach = cleaned_data.get('coach')
        
        if not team:
            raise forms.ValidationError("Team is required")
        if not coach:
            raise forms.ValidationError("Coach is required")
            
        return cleaned_data

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
            self.fields['player'].required = True
            self.fields['batting_order'].required = True
            self.fields['positions_by_inning'].required = True

    def clean(self):
        cleaned_data = super().clean()
        batting_order = cleaned_data.get('batting_order')
        positions = cleaned_data.get('positions_by_inning')
        player = cleaned_data.get('player')
        
        if not player:
            raise forms.ValidationError("Player is required")
        
        if batting_order is not None and batting_order < 1:
            raise forms.ValidationError("Batting order must be at least 1")
        
        if positions:
            try:
                # Handle both string and dictionary inputs
                if isinstance(positions, str):
                    positions_dict = json.loads(positions)
                else:
                    positions_dict = positions
                
                if not isinstance(positions_dict, dict):
                    raise forms.ValidationError("Positions must be a valid dictionary")
            except json.JSONDecodeError:
                raise forms.ValidationError("Invalid positions format")
        
        return cleaned_data

class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['game_id', 'team_home', 'team_away', 'date', 'time', 'location', 'finalized', 'is_verified']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        team_home = kwargs.pop('team_home', None)
        super().__init__(*args, **kwargs)
        if team_home:
            # Only show teams from the same division
            self.fields['team_away'].queryset = Team.objects.filter(
                division=team_home.division
            ).exclude(id=team_home.id)

class LeagueForm(forms.ModelForm):
    class Meta:
        model = League
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class DivisionForm(forms.ModelForm):
    class Meta:
        model = Division
        fields = ['name', 'league', 'is_open', 'coordinators']
        widgets = {
            'coordinators': forms.SelectMultiple(attrs={'class': 'select2'}),
        }

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'country', 'city', 'province_state', 'is_approved', 'division', 'coaches', 'max_players']
        widgets = {
            'coaches': forms.SelectMultiple(attrs={'class': 'select2'}),
            'max_players': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'division': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['division'].required = True
        self.fields['max_players'].required = True

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        division = cleaned_data.get('division')
        max_players = cleaned_data.get('max_players')

        if not name:
            raise forms.ValidationError("Team name is required")
        
        if not division:
            raise forms.ValidationError("Division is required")
        
        if max_players and max_players < 1:
            raise forms.ValidationError("Maximum players must be at least 1")

        return cleaned_data


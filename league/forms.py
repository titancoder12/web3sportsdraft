# league/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Player, Division, Team, JoinTeamRequest

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

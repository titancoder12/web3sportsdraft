# league/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Player, Division, Team

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
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    division = forms.ModelChoiceField(
        queryset=Division.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
        empty_label="-- Select a Division --"
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'division', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Player.objects.create(
                user=user,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                division=self.cleaned_data['division']  # Assign selected division
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
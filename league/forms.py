# league/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Player

# league/forms.py
class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'age', 'position', 'rating', 'division']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
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
        self.fields['division'].required = True  # Ensure division is set

class PlayerProfileForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'age', 'position', 'description']  # No coach_comments
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
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
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))

    class Meta:
        model = User
        fields = ['username', 'name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Player.objects.create(
                user=user,
                name=self.cleaned_data['name']
            )
        return user
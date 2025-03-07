# league/forms.py
from django import forms
from .models import Player

class PlayerForm(forms.ModelForm):  # For admins/coaches adding players
    class Meta:
        model = Player
        fields = ['name', 'age', 'position', 'rating']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 5, 'max': 18}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['age'].required = False
        self.fields['position'].required = False
        self.fields['rating'].required = False

class PlayerProfileForm(forms.ModelForm):  # For players updating their own info
    class Meta:
        model = Player
        fields = ['name', 'age', 'position']  # Exclude rating, team, draft_round
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 5, 'max': 18}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['age'].required = False
        self.fields['position'].required = False
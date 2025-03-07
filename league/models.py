# league/models.py
from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    name = models.CharField(max_length=100)
    coaches = models.ManyToManyField(User, related_name='teams')
    max_players = models.IntegerField(default=12)

    def __str__(self):
        return self.name

class Player(models.Model):
    name = models.CharField(max_length=100)  # Required field
    age = models.IntegerField(null=True, blank=True)  # Optional
    position = models.CharField(max_length=50, blank=True)  # Optional, no null since it's a CharField
    rating = models.IntegerField(default=0, blank=True)  # Optional with default
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL)
    draft_round = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

class DraftPick(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    pick_number = models.IntegerField()
    round_number = models.IntegerField()

    class Meta:
        ordering = ['pick_number']

    def __str__(self):
        return f"Pick {self.pick_number}: {self.player} to {self.team}"
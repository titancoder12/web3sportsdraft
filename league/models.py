# league/models.py
from django.db import models
from django.contrib.auth.models import User

class League(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Division(models.Model):
    name = models.CharField(max_length=100)
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='divisions')

    def __str__(self):
        return f"{self.league.name} - {self.name}"

class Team(models.Model):
    name = models.CharField(max_length=100)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='teams', null=True)
    coaches = models.ManyToManyField(User, related_name='teams')
    max_players = models.IntegerField(default=12)

    def __str__(self):
        return f"{self.name} ({self.division})"

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='player_profile')
    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    position = models.CharField(max_length=50, blank=True)
    rating = models.IntegerField(default=0, blank=True)
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL)
    draft_round = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    coach_comments = models.TextField(blank=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='players',null=True)  # Scope players to division

    def __str__(self):
        return f"{self.name} ({self.division})"

class DraftPick(models.Model):
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='draft_picks', null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    pick_number = models.IntegerField()
    round_number = models.IntegerField()

    class Meta:
        ordering = ['pick_number']

    def __str__(self):
        return f"Pick {self.pick_number}: {self.player} to {self.team} ({self.division})"
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
    is_open = models.BooleanField(default=False)
    coordinators = models.ManyToManyField(User, related_name='coordinated_divisions', blank=True)

    def __str__(self):
        return f"{self.league.name} - {self.name}"

class Team(models.Model):
    name = models.CharField(max_length=100)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='teams')
    coaches = models.ManyToManyField(User, related_name='teams')
    max_players = models.IntegerField(default=12)

    def __str__(self):
        return f"{self.name} ({self.division})"

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='player_profile')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    birth_country = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=50, blank=True)
    rating = models.IntegerField(default=0, blank=True)
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL)
    draft_round = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    coach_comments = models.TextField(blank=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='players')

    number = models.IntegerField(null=True, blank=True)
    batting_throwing = models.CharField(max_length=10, blank=True)  # "B/T" Field
    height_weight = models.CharField(max_length=20, blank=True)  # "H/W" Field

    # Performance Evaluations
    grip_strength = models.FloatField(null=True, blank=True)
    lateral_jump = models.FloatField(null=True, blank=True)
    shot_put = models.FloatField(null=True, blank=True)
    five_ten_five_yards = models.FloatField(null=True, blank=True)  # 5-10-5 Yards
    ten_yards = models.FloatField(null=True, blank=True)
    catcher_pop = models.FloatField(null=True, blank=True)
    fielding_notes = models.TextField(blank=True)
    exit_velo = models.FloatField(null=True, blank=True)
    bat_speed = models.FloatField(null=True, blank=True)
    pitching_comment = models.TextField(blank=True)

    # Personal Details
    birthdate = models.DateField(null=True, blank=True)
    parents_volunteering = models.CharField(max_length=255, blank=True)
    other_activities = models.CharField(max_length=255, blank=True)
    volunteering_comments = models.TextField(blank=True)
    primary_positions = models.CharField(max_length=255, blank=True)
    secondary_positions = models.CharField(max_length=255, blank=True)
    throwing = models.CharField(max_length=50, blank=True)  # e.g., "Right", "Left"
    batting = models.CharField(max_length=50, blank=True)  # e.g., "Right", "Left"
    school = models.CharField(max_length=100, blank=True)
    grade_level = models.CharField(max_length=50, blank=True)
    travel_teams = models.CharField(max_length=255, blank=True)
    travel_why = models.CharField(max_length=255, blank=True)
    travel_years = models.IntegerField(null=True, blank=True)
    personal_comments = models.TextField(blank=True)
    past_level = models.CharField(max_length=100, blank=True)
    travel_before = models.CharField(max_length=255, blank=True)
    last_team = models.CharField(max_length=100, blank=True)
    last_league = models.CharField(max_length=225, blank=True)
    conflict_description = models.TextField(blank=True)
    last_team_coach = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.division})"

class DraftPick(models.Model):
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='draft_picks')
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    pick_number = models.IntegerField()
    round_number = models.IntegerField()

    class Meta:
        ordering = ['pick_number']

    def __str__(self):
        return f"Pick {self.pick_number}: {self.player} to {self.team} ({self.division})"
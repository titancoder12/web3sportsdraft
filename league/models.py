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
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    province_state = models.CharField(max_length=100, blank=True)
    is_approved = models.BooleanField(default=False)
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
    teams = models.ManyToManyField(Team, blank=True, related_name='players')  # will eventually replace team. For now for an easier migration to many-to-many.
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
    
from django.db import models

class Game(models.Model):
    game_id = models.CharField(max_length=50, unique=True)
    team_home = models.ForeignKey("Team", on_delete=models.CASCADE, related_name="home_games")
    team_away = models.ForeignKey("Team", on_delete=models.CASCADE, related_name="away_games")
    date = models.DateTimeField()
    time = models.TimeField()
    location = models.CharField(max_length=100)
    finalized = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

class PlayerGameStat(models.Model):
    player = models.ForeignKey("Player", on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    at_bats = models.IntegerField(default=0)
    runs = models.IntegerField(default=0)
    hits = models.IntegerField(default=0)
    rbis = models.IntegerField(default=0)
    singles = models.IntegerField(default=0)
    doubles = models.IntegerField(default=0)
    triples = models.IntegerField(default=0)
    home_runs = models.IntegerField(default=0)
    strikeouts = models.IntegerField(default=0)
    base_on_balls = models.IntegerField(default=0)
    hit_by_pitch = models.IntegerField(default=0)
    sacrifice_flies = models.IntegerField(default=0)
    innings_pitched = models.FloatField(default=0)
    hits_allowed = models.IntegerField(default=0)
    runs_allowed = models.IntegerField(default=0)
    earned_runs = models.IntegerField(default=0)
    walks_allowed = models.IntegerField(default=0)
    strikeouts_pitching = models.IntegerField(default=0)
    home_runs_allowed = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)

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
    

class TeamLog(models.Model):
    team = models.ForeignKey("Team", on_delete=models.CASCADE)
    coach = models.ForeignKey(User, on_delete=models.CASCADE)
    log_type = models.CharField(max_length=10, choices=[("practice", "Practice"), ("game", "Game")])
    date = models.DateField()
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']



# league/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class League(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    coordinators = models.ManyToManyField(User, related_name='coordinated_leagues')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

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
        return f"{self.name}"

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='player_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
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
    division = models.ForeignKey(Division, on_delete=models.CASCADE, null=True, blank=True, related_name='players')
    number = models.IntegerField(null=True, blank=True)
    batting_throwing = models.CharField(max_length=10, blank=True)  # "B/T" Field
    height_weight = models.CharField(max_length=20, blank=True)  # "H/W" Field
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
    parent_name = models.CharField(max_length=100, blank=True)
    parent_email = models.EmailField(blank=True)
    parent_phone = models.CharField(max_length=20, blank=True)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.get_full_name()

class PerformanceEvaluation(models.Model):
    player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='evaluations')
    date = models.DateField(auto_now_add=True)

    grip_strength = models.FloatField(null=True, blank=True)
    lateral_jump = models.FloatField(null=True, blank=True)
    shot_put = models.FloatField(null=True, blank=True)
    five_ten_five_yards = models.FloatField(null=True, blank=True)
    ten_yards = models.FloatField(null=True, blank=True)
    catcher_pop = models.FloatField(null=True, blank=True)
    fielding_notes = models.TextField(blank=True)
    exit_velo = models.FloatField(null=True, blank=True)
    bat_speed = models.FloatField(null=True, blank=True)
    pitching_comment = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

from datetime import datetime
class Game(models.Model):
    game_id = models.CharField(max_length=50, unique=True)
    team_home = models.ForeignKey("Team", on_delete=models.CASCADE, null=True, related_name="home_games")
    team_away = models.ForeignKey("Team", on_delete=models.CASCADE, null=True, related_name="away_games")
    date = models.DateTimeField()
    time = models.TimeField()
    location = models.CharField(max_length=100)
    finalized = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        date_str = self.date.strftime("%Y-%m-%d") if self.date else "Unknown Date" 
        return f"{self.team_away} vs {self.team_home} {date_str}"

class PlayerGameStat(models.Model):
    player = models.ForeignKey("Player", on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    source = models.CharField(max_length=20, choices=[('self', 'Self'), ('coach', 'Coach')], default='coach')

    # Stats: 
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


class PlayerLog(models.Model):
    player = models.ForeignKey("Player", on_delete=models.CASCADE)
    team = models.ForeignKey("Team", on_delete=models.CASCADE)
    coach = models.ForeignKey(User, on_delete=models.CASCADE)
    log_type = models.CharField(max_length=10, choices=[
        ("practice", "Practice"),
        ("game", "Game"),
        ("training", "Training"),
    ])
    date = models.DateField()
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Player Log"
        verbose_name_plural = "Player Logs"

    def __str__(self):
        return f"{self.date} - {self.player} - {self.log_type}"
    

class PlayerNote(models.Model):
    player = models.OneToOneField("Player", on_delete=models.CASCADE, related_name="notes")
    content = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notes for {self.player}"

class PlayerJournalEntry(models.Model):
    player = models.ForeignKey("Player", on_delete=models.CASCADE, related_name="journal_entries")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Journal Entry on {self.created_at:%Y-%m-%d}"
    

class JoinTeamRequest(models.Model):
    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    team = models.ForeignKey('Team', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('player', 'team')  # Prevent duplicates

    def __str__(self):
        return f"{self.player} requests to join {self.team}"
    

class SignInLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='signin_logs')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} signed in at {self.timestamp}"

class FairPlayRuleSet(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='fair_play_rules')
    age_group = models.CharField(max_length=10)  # e.g., "11U"
    min_innings_per_player = models.IntegerField(default=0)
    max_consecutive_bench_innings = models.IntegerField(default=0)
    min_plate_appearances = models.IntegerField(default=0)
    enforce_plate_appearance = models.BooleanField(default=False)
    enforce_position_rotation = models.BooleanField(default=False)
    max_innings_per_position = models.JSONField(default=dict)  # e.g., {"C": 3, "P": 3}
    eh_option_start_date = models.DateField(null=True, blank=True)
    eh_option_end_date = models.DateField(null=True, blank=True)
    no_mandated_fair_play = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.league.name} - {self.age_group} Rules"

class PlayerAvailability(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('injured', 'Injured')
    ]
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='availability')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='player_availability')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('player', 'game')
        verbose_name_plural = "Player Availabilities"

    def __str__(self):
        return f"{self.player} - {self.game} - {self.status}"

class LineupPlan(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='lineup_plans')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='lineup_plans', null=True, blank=True)
    coach = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_lineups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_final = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        game_str = f" vs {self.game.team_away}" if self.game else " (Practice)"
        return f"{self.team.name}{game_str} - {self.created_at.strftime('%Y-%m-%d')}"

class LineupEntry(models.Model):
    lineup_plan = models.ForeignKey(LineupPlan, on_delete=models.CASCADE, related_name='entries')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='lineup_entries')
    batting_order = models.IntegerField()
    positions_by_inning = models.JSONField(default=dict)  # e.g., {"1": "C", "2": "P", "3": "1B"}
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            ('lineup_plan', 'batting_order'),
            ('lineup_plan', 'player')
        ]
        ordering = ['batting_order']

    def __str__(self):
        return f"{self.player} - Batting {self.batting_order}"

class LineupCompliance(models.Model):
    lineup_plan = models.ForeignKey(LineupPlan, on_delete=models.CASCADE, related_name='compliance_checks')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='compliance_checks')
    innings_played = models.IntegerField(default=0)
    consecutive_bench_innings = models.IntegerField(default=0)
    plate_appearances = models.IntegerField(default=0)
    position_violations = models.JSONField(default=dict)  # e.g., {"C": 4} for exceeding max innings
    is_compliant = models.BooleanField(default=True)
    violation_details = models.TextField(blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('lineup_plan', 'player')

    def __str__(self):
        return f"{self.player} - {self.lineup_plan} - {'Compliant' if self.is_compliant else 'Non-compliant'}"





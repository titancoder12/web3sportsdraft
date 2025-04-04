# league/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse  # Ensure this line is present
from .models import Team, Player, DraftPick, Division, PlayerGameStat, Game, PlayerLog, PlayerNote, PlayerJournalEntry, PerformanceEvaluation
from django.contrib.auth.decorators import login_required
from .forms import PlayerForm, PlayerProfileForm, PlayerSignupForm, CoachCommentForm, PlayerCSVUploadForm
from django.contrib.auth.models import User
import csv
from io import TextIOWrapper
from datetime import datetime
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce

from collections import defaultdict
from league.models import TeamLog, JoinTeamRequest

from django.utils import timezone
from django.http import HttpResponseForbidden
from django.contrib.auth import login


from django.contrib.auth import login
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string

from .forms import PlayerSignupForm, JoinTeamRequestForm, PlayerGameStatForm
from threading import Thread
from django.contrib import messages
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'registration/activation_success.html', {'user': user})
    else:
        return render(request, 'registration/activation_invalid.html')


@login_required
def player_teams_view(request):
    player = request.user.player_profile  # assumes OneToOneField to User
    teams = player.teams.prefetch_related("coaches", "players", "division")

    return render(request, "league/player_teams.html", {
        "player": player,
        "teams": teams,
    })

@login_required
def player_evaluations(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    user = request.user

    # Rule 1: Players can only access their own
    if hasattr(user, 'player_profile') and user.player_profile.id == player.id:
        pass

    # Rule 2: Coaches can access only players on teams they coach
    elif user.teams.exists():
        # Teams this coach coaches
        coach_team_ids = user.teams.values_list("id", flat=True)
        # Check if player is on any of those teams
        if not player.teams.filter(id__in=coach_team_ids).exists():
            return HttpResponseForbidden("You do not have permission to view this player's evaluations.")
    else:
        return HttpResponseForbidden("You do not have permission to view this player's evaluations.")

    # Access granted → show evaluations
    evaluations = player.evaluations.all().order_by("-date")

    is_self = hasattr(user, 'player_profile') and user.player_profile.id == player.id # Add a flag to indicate if this is the player's own view


    return render(request, "league/player_evaluations.html", {
        "player": player,
        "evaluations": evaluations,
        "is_self": is_self,
    })

@login_required
def get_evaluation_detail(request, player_id, evaluation_id):
    evaluation = get_object_or_404(PerformanceEvaluation, id=evaluation_id, player_id=player_id)

    data = {
        'date': evaluation.date,
        'grip_strength': evaluation.grip_strength,
        'exit_velo': evaluation.exit_velo,
        'bat_speed': evaluation.bat_speed,
        'shot_put': evaluation.shot_put,
        'lateral_jump': evaluation.lateral_jump,
        'ten_yards': evaluation.ten_yards,
        'five_ten_five_yards': evaluation.five_ten_five_yards,
        'catcher_pop': evaluation.catcher_pop,
        'fielding_notes': evaluation.fielding_notes,
        'pitching_comment': evaluation.pitching_comment,
    }
    return JsonResponse(data)


@login_required
def player_logs_view(request):
    if not hasattr(request.user, 'player_profile'):
        return redirect('dashboard')

    player = request.user.player_profile
    teams = player.teams.all()

    # Fetch logs
    team_logs = TeamLog.objects.filter(team__in=teams).select_related("team", "coach")
    player_logs = PlayerLog.objects.filter(player=player).select_related("team", "coach")

    # Handle note save
    #note, _ = PlayerNote.objects.get_or_create(player=player)
    #if request.method == "POST":
    #    note.content = request.POST.get("note", "")
    #    note.save()
    #    return redirect("player_logs")
    

    if request.method == "POST":
        content = request.POST.get("note", "").strip()
        if content:
            PlayerJournalEntry.objects.create(player=player, content=content)
        return redirect("player_logs")

    journal_entries = PlayerJournalEntry.objects.filter(player=player).order_by("-created_at")

    return render(request, "league/player_logs.html", {
        "player": player,
        "team_logs": team_logs,
        "player_logs": player_logs,
        #"player_note": note,
        "journal_entries": journal_entries,
    })


@login_required
def coordinator_team_logs(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    user = request.user

    # Check if user is a coordinator of this team's division OR a coach of this team
    is_coordinator = team.division.coordinators.filter(id=user.id).exists()
    is_coach = team.coaches.filter(id=user.id).exists()

    if not (is_coordinator or is_coach):
        return render(request, "league/no_permission.html", {
            "message": "You do not have access to this team's logs."
        })

    logs = TeamLog.objects.filter(team=team).select_related("coach").order_by("-date")

    return render(request, "league/coordinator_team_logs.html", {
        "team": team,
        "logs": logs,
        "is_coordinator": is_coordinator,
        "is_coach": is_coach,
    })

@login_required
def delete_player_log(request, log_id):
    log = get_object_or_404(PlayerLog, id=log_id, coach=request.user)
    player_id = log.player.id
    if request.method == "POST":
        log.delete()
    return redirect("coach_player_detail", player_id=player_id)


@login_required
def edit_player_log(request, log_id):
    log = get_object_or_404(PlayerLog, id=log_id, coach=request.user)
    if request.method == "POST":
        log.log_type = request.POST.get("log_type")
        log.date = request.POST.get("date")
        log.notes = request.POST.get("notes")
        log.save()
        return redirect("coach_player_detail", player_id=log.player.id)

    return render(request, "league/edit_player_log.html", {
        "log": log
    })


@login_required
def add_player_log(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    user = request.user
    team_id = request.POST.get("team_id")

    # Make sure the coach is allowed to log for this team
    team = get_object_or_404(Team, id=team_id, coaches=user)

    if request.method == "POST":
        PlayerLog.objects.create(
            player=player,
            team=team,
            coach=user,
            log_type=request.POST.get("log_type"),
            date=request.POST.get("date"),
            notes=request.POST.get("notes"),
        )
    return redirect("coach_player_detail", player_id=player.id)


@login_required
def coach_player_detail(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    user = request.user

    # Get teams this coach has coached
    coached_teams = user.teams.all()

    # Logs: only from teams the coach coached
    visible_logs = PlayerLog.objects.filter(
        player=player,
        team__in=coached_teams
    ).select_related('coach', 'team')

    # Teams this coach coached AND the player was on
    shared_teams = player.teams.filter(id__in=coached_teams.values_list("id", flat=True))

    # === Per-Team Stats ===
    team_stats = []
    for team in shared_teams:
        stats_qs = PlayerGameStat.objects.filter(player=player).filter(
            game__team_home=team
        ) | PlayerGameStat.objects.filter(
            player=player,
            game__team_away=team
        )

        stats = stats_qs.aggregate(
            games_played=Count('game', distinct=True),
            at_bats=Sum('at_bats'),
            hits=Sum('hits'),
            runs=Sum('runs'),
            rbis=Sum('rbis'),
            home_runs=Sum('home_runs'),
            base_on_balls=Sum('base_on_balls'),
            strikeouts=Sum('strikeouts'),
            innings_pitched=Sum('innings_pitched'),
            earned_runs=Sum('earned_runs'),
        )

        ab = stats['at_bats'] or 0
        hits = stats['hits'] or 0
        bb = stats['base_on_balls'] or 0
        slg = hits  # Replace with total bases for real SLG
        obp = (hits + bb) / (ab + bb) if (ab + bb) > 0 else 0
        avg = hits / ab if ab > 0 else 0
        ops = obp + slg
        era = (stats['earned_runs'] or 0) * 9 / (stats['innings_pitched'] or 1)

        team_stats.append({
            'team': team,
            'games_played': stats['games_played'] or 0,
            'at_bats': ab,
            'hits': hits,
            'runs': stats['runs'] or 0,
            'rbis': stats['rbis'] or 0,
            'home_runs': stats['home_runs'] or 0,
            'base_on_balls': bb,
            'strikeouts': stats['strikeouts'] or 0,
            'avg': f"{avg:.3f}",
            'obp': f"{obp:.3f}",
            'slg': f"{slg:.3f}",
            'ops': f"{ops:.3f}",
            'era': f"{era:.2f}",
        })

    # === Overall Stats ===
    overall_stats_qs = PlayerGameStat.objects.filter(
        player=player,
        game__team_home__in=shared_teams
    ) | PlayerGameStat.objects.filter(
        player=player,
        game__team_away__in=shared_teams
    )

    overall = overall_stats_qs.aggregate(
        games_played=Count('game', distinct=True),
        at_bats=Sum('at_bats'),
        hits=Sum('hits'),
        runs=Sum('runs'),
        rbis=Sum('rbis'),
        home_runs=Sum('home_runs'),
        base_on_balls=Sum('base_on_balls'),
        strikeouts=Sum('strikeouts'),
        innings_pitched=Sum('innings_pitched'),
        earned_runs=Sum('earned_runs'),
    )

    ab = overall['at_bats'] or 0
    hits = overall['hits'] or 0
    bb = overall['base_on_balls'] or 0
    slg = hits  # Replace with total bases for real SLG
    obp = (hits + bb) / (ab + bb) if (ab + bb) > 0 else 0
    avg = hits / ab if ab > 0 else 0
    ops = obp + slg
    era = (overall['earned_runs'] or 0) * 9 / (overall['innings_pitched'] or 1)

    overall_stats = {
        'games_played': overall['games_played'] or 0,
        'at_bats': ab,
        'hits': hits,
        'runs': overall['runs'] or 0,
        'rbis': overall['rbis'] or 0,
        'home_runs': overall['home_runs'] or 0,
        'base_on_balls': bb,
        'strikeouts': overall['strikeouts'] or 0,
        'avg': f"{avg:.3f}",
        'obp': f"{obp:.3f}",
        'slg': f"{slg:.3f}",
        'ops': f"{ops:.3f}",
        'era': f"{era:.2f}",
    }

    evaluations = PerformanceEvaluation.objects.filter(player=player).order_by("-date")

    return render(request, "league/coach_player_detail.html", {
        "player": player,
        "visible_logs": visible_logs,
        "shared_teams": shared_teams,
        "team_stats": team_stats,
        "overall_stats": overall_stats,
         "evaluations": evaluations,  # ✅ Add this line
    })

@login_required
def edit_team_log(request, log_id):
    log = get_object_or_404(TeamLog, id=log_id, coach=request.user)
    if request.method == "POST":
        log.log_type = request.POST.get("log_type")
        log.date = request.POST.get("date")
        log.notes = request.POST.get("notes")
        log.save()
        return redirect("team_logs", team_id=log.team.id)

    return render(request, "league/edit_team_log.html", {"log": log})

@login_required
def delete_team_log(request, log_id):
    log = get_object_or_404(TeamLog, id=log_id, coach=request.user)
    team_id = log.team.id
    if request.method == "POST":
        log.delete()
    return redirect("team_logs", team_id=team_id)


@login_required
def team_logs_view(request, team_id):
    team = get_object_or_404(Team, id=team_id, coaches=request.user)
    logs = TeamLog.objects.filter(team=team).order_by('-date')

    return render(request, "league/team_logs.html", {
        "team": team,
        "logs": logs,
    })


@login_required
def add_team_log(request, team_id):
    team = get_object_or_404(Team, id=team_id, coaches=request.user)

    if request.method == "POST":
        TeamLog.objects.create(
            team=team,
            coach=request.user,
            log_type=request.POST.get("log_type"),
            date=request.POST.get("date"),
            notes=request.POST.get("notes"),
        )
    return redirect("team_logs", team_id=team.id)

@login_required
def coach_dashboard(request):
    user = request.user
    teams = user.teams.prefetch_related("players", "division")

    # Get unique divisions from coach's teams
    division_ids = teams.values_list("division_id", flat=True).distinct()
    divisions = Division.objects.filter(id__in=division_ids)

    # Get logs only for teams this coach is on
    team_logs = TeamLog.objects.filter(team__in=teams).select_related("team", "coach")

    # Group games by team
    games_by_team = defaultdict(list)
    for team in teams:
        team_games = Game.objects.filter(team_home=team) | Game.objects.filter(team_away=team)
        team_games = team_games.order_by('-date').select_related('team_home', 'team_away')
        games_by_team[team.id] = team_games


    # Get pending join requests for any of the coach's teams
    pending_requests = JoinTeamRequest.objects.filter(
        team__in=teams,
        is_approved=None
    ).select_related('player', 'team')


    print("Coach teams:", list(request.user.teams.all()))
    print("Pending requests:", list(pending_requests))

    return render(request, "league/coach_dashboard.html", {
        "teams": teams,
        "divisions": divisions,
        "team_logs": team_logs,
         "games_by_team": games_by_team,
        "pending_requests": pending_requests,
    })

@login_required
def player_dashboard(request):
    user = request.user

    try:
        player = user.player_profile
    except:
        return render(request, "league/player_dashboard.html", {
            "error": "Your account is not associated with a player profile."
        })
    

    # Get pending join requests
    pending_requests = JoinTeamRequest.objects.filter(
        player=player,
        is_approved=None
    ).select_related('team')

    rejected_requests = JoinTeamRequest.objects.filter(
        player=player,
        is_approved=False
    ).select_related('team')


    # Self-entered stats, Verified stats, and General stats
    verified_stats = PlayerGameStat.objects.filter(player=player, is_verified=True)
    general_stats = PlayerGameStat.objects.filter(player=player)



    # Game stats for the player
    game_stats = PlayerGameStat.objects.select_related("game").filter(player=player).order_by("-game__date")

    # Group stats by team (for Game History by Team)
    team_games = defaultdict(list)
    player_team_ids = set(player.teams.values_list("id", flat=True))

    for stat in game_stats:
        home_id = stat.game.team_home_id
        away_id = stat.game.team_away_id

        if home_id in player_team_ids:
            team_games[stat.game.team_home.name].append(stat)
        elif away_id in player_team_ids:
            team_games[stat.game.team_away.name].append(stat)

    # Overall aggregate stats
    agg = game_stats.aggregate(
        at_bats=Coalesce(Sum("at_bats"), 0),
        hits=Coalesce(Sum("hits"), 0),
        runs=Coalesce(Sum("runs"), 0),
        rbis=Coalesce(Sum("rbis"), 0),
        home_runs=Coalesce(Sum("home_runs"), 0),
        strikeouts=Coalesce(Sum("strikeouts"), 0),
        base_on_balls=Coalesce(Sum("base_on_balls"), 0),
        hit_by_pitch=Coalesce(Sum("hit_by_pitch"), 0),
        sacrifice_flies=Coalesce(Sum("sacrifice_flies"), 0),
        doubles=Coalesce(Sum("doubles"), 0),
        triples=Coalesce(Sum("triples"), 0),
        singles=Coalesce(Sum("singles"), 0),
        earned_runs=Coalesce(Sum("earned_runs"), 0),
        innings_pitched=Coalesce(Sum("innings_pitched"), 0.0),
        walks_allowed=Coalesce(Sum("walks_allowed"), 0),
        strikeouts_pitching=Coalesce(Sum("strikeouts_pitching"), 0),
    )

    ab = agg["at_bats"] or 1
    avg = round(agg["hits"] / ab, 3)
    tb = agg["singles"] + 2 * agg["doubles"] + 3 * agg["triples"] + 4 * agg["home_runs"]
    slg = round(tb / ab, 3)
    obp_denom = ab + agg["base_on_balls"] + agg["hit_by_pitch"] + agg["sacrifice_flies"] or 1
    obp = round((agg["hits"] + agg["base_on_balls"] + agg["hit_by_pitch"]) / obp_denom, 3)
    ops = round(obp + slg, 3)
    era = round((agg["earned_runs"] * 9) / agg["innings_pitched"], 2) if agg["innings_pitched"] else 0
    kbb = round(agg["strikeouts_pitching"] / agg["walks_allowed"], 2) if agg["walks_allowed"] else 0

    # Per-team stat summaries
    team_stats = []
    for team in player.teams.all():
        team_game_stats = game_stats.filter(
            game__team_home=team
        ) | game_stats.filter(
            game__team_away=team
        )

        team_agg = team_game_stats.aggregate(
            games_played=Count("game", distinct=True),
            hits=Coalesce(Sum("hits"), 0),
            at_bats=Coalesce(Sum("at_bats"), 0),
            rbis=Coalesce(Sum("rbis"), 0),
            home_runs=Coalesce(Sum("home_runs"), 0),
            base_on_balls=Coalesce(Sum("base_on_balls"), 0),
            hit_by_pitch=Coalesce(Sum("hit_by_pitch"), 0),
            sacrifice_flies=Coalesce(Sum("sacrifice_flies"), 0),
            doubles=Coalesce(Sum("doubles"), 0),
            triples=Coalesce(Sum("triples"), 0),
            singles=Coalesce(Sum("singles"), 0),
            earned_runs=Coalesce(Sum("earned_runs"), 0),
            innings_pitched=Coalesce(Sum("innings_pitched"), 0.0),
        )

        tab = team_agg["at_bats"] or 1
        team_tb = team_agg["singles"] + 2 * team_agg["doubles"] + 3 * team_agg["triples"] + 4 * team_agg["home_runs"]
        team_slg = round(team_tb / tab, 3)

        team_obp_denom = tab + team_agg["base_on_balls"] + team_agg["hit_by_pitch"] + team_agg["sacrifice_flies"] or 1
        team_obp = round((team_agg["hits"] + team_agg["base_on_balls"] + team_agg["hit_by_pitch"]) / team_obp_denom, 3)

        team_ops = round(team_obp + team_slg, 3)
        team_avg = round(team_agg["hits"] / tab, 3)
        team_era = round((team_agg["earned_runs"] * 9) / team_agg["innings_pitched"], 2) if team_agg["innings_pitched"] else 0

        team_stats.append({
            "team_name": team.name,
            "games_played": team_agg["games_played"],
            "hits": team_agg["hits"],
            "at_bats": team_agg["at_bats"],
            "avg": team_avg,
            "rbis": team_agg["rbis"],
            "home_runs": team_agg["home_runs"],
            "slg": team_slg,
            "obp": team_obp,
            "ops": team_ops,
            "era": team_era,
        })

    return render(request, "league/player_dashboard.html", {
        "player": player,
        "game_stats": game_stats,
        "team_games": dict(team_games),
        "overall_stats": agg,
        "batting_avg": avg,
        "slg": slg,
        "obp": obp,
        "ops": ops,
        "era": era,
        "kbb": kbb,
        "team_stats": team_stats,
        "pending_requests": pending_requests,
        "rejected_requests": rejected_requests,
    })

def box_score_view(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    home_team_stats = PlayerGameStat.objects.filter(game=game, player__teams=game.team_home)
    away_team_stats = PlayerGameStat.objects.filter(game=game, player__teams=game.team_away)

    context = {
        'game': game,
        'home_team_stats': home_team_stats,
        'away_team_stats': away_team_stats,
        "back_url": request.META.get("HTTP_REFERER", "/"),
    }
    return render(request, 'league/box_score.html', context)


@login_required
def import_players(request):
    # Restrict to superusers or coordinators
    if not (request.user.is_superuser or Division.objects.filter(coordinators=request.user).exists()):
        messages.error(request, "You do not have permission to import players.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = PlayerCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
            division = form.cleaned_data['division']
            reader = csv.DictReader(csv_file)

            # Field mapping
            field_mapping = {
                'first_name': 'first_name',
                'last_name': 'last_name',
                'birthdate': 'birthdate',
                'grip_strength': 'grip_strength',
                'lateral_jump': 'lateral_jump',
                'shot_put': 'shot_put',
                'five_ten_five_yards': 'five_ten_five_yards',
                'ten_yards': 'ten_yards',
                'catcher_pop': 'catcher_pop',
                'fielding_notes': 'fielding_notes',
                'exit_velo': 'exit_velo',
                'bat_speed': 'bat_speed',
                'pitching_comment': 'pitching_comment',
                'parents_volunteering': 'parents_volunteering',
                'other_activities': 'other_activities',
                'volunteering_comments': 'volunteering_comments',
                'primary_positions': 'primary_positions',
                'secondary_positions': 'secondary_positions',
                'throwing': 'throwing',
                'batting': 'batting',
                'school': 'school',
                'grade_level': 'grade_level',
                'travel_teams': 'travel_teams',
                'travel_why': 'travel_why',
                'travel_years': 'travel_years',
                'personal_comments': 'personal_comments',
                'past_level': 'past_level',
                'travel_before': 'travel_before',
                'last_team': 'last_team',
                'last_league': 'last_league',
                'conflict_description': 'conflict_description',
                'last_team_coach': 'last_team_coach',
            }

            try:
                for row in reader:
                    # Generate username
                    base_username = (row['first_name'] + row['last_name']).lower()
                    username = base_username
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username}{counter}"
                        counter += 1

                    # Generate default password from birthdate
                    birthdate_str = row.get('birthdate', '')
                    if birthdate_str:
                        try:
                            birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d')
                            default_password = birthdate.strftime('%Y%m%d')  # e.g., "20100515"
                        except ValueError:
                            messages.warning(request, f"Invalid birthdate format for {row['first_name']} {row['last_name']}, skipping.")
                            continue
                    else:
                        messages.warning(request, f"No birthdate for {row['first_name']} {row['last_name']}, skipping.")
                        continue

                    # Create User
                    user = User.objects.create_user(
                        username=username,
                        password=default_password,
                        first_name=row['first_name'],
                        last_name=row['last_name']
                    )

                    # Prepare player data
                    player_data = {'division': division}
                    for csv_field, model_field in field_mapping.items():
                        if csv_field in row and row[csv_field]:
                            if csv_field == 'birthdate':
                                player_data[model_field] = birthdate
                            elif csv_field in ['grip_strength', 'lateral_jump', 'shot_put', 'five_ten_five_yards', 'ten_yards', 'catcher_pop', 'exit_velo', 'bat_speed']:
                                player_data[model_field] = float(row[csv_field]) if row[csv_field] else None
                            elif csv_field == 'travel_years':
                                player_data[model_field] = int(row[csv_field]) if row[csv_field] else None
                            else:
                                player_data[model_field] = row[csv_field]

                    # Create Player
                    Player.objects.create(user=user, **player_data)
                    messages.success(request, f"Imported {row['first_name']} {row['last_name']} as {username}")

                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f"Error importing players: {str(e)}")
    else:
        form = PlayerCSVUploadForm()

    return render(request, 'league/import_players.html', {'form': form})


@login_required
def player_detail(request, player_id):
    user = request.user
    player = get_object_or_404(Player, id=player_id)

    # Coach access: Is user a coach of any of the player's teams?
    player_team_ids = player.teams.values_list("id", flat=True)
    is_coach = Team.objects.filter(id__in=player_team_ids, coaches=user).exists()

    # Coordinator access: Is user a coordinator of the player's division?
    is_coordinator = player.division.coordinators.filter(id=user.id).exists()

    if not (is_coach or is_coordinator):
        return render(request, "league/no_permission.html", {
            "message": "You do not have access to this player's details."
        })

    # Get teams in the player's division
    teams_in_division = Team.objects.filter(division=player.division)
    team_ids_in_division = teams_in_division.values_list("id", flat=True)

    # Logs for this player, limited to teams in this division
    player_logs = PlayerLog.objects.filter(
        player=player,
        team_id__in=team_ids_in_division
    ).select_related("team", "coach")

    # Filter to only player's teams in this division
    player_division_teams = player.teams.filter(id__in=team_ids_in_division)

    # === Per-Team Stats ===
    team_stats = []
    for team in player_division_teams:
        stats_qs = PlayerGameStat.objects.filter(player=player).filter(
            game__team_home=team
        ) | PlayerGameStat.objects.filter(
            player=player,
            game__team_away=team
        )

        stats = stats_qs.aggregate(
            games_played=Count('game', distinct=True),
            at_bats=Sum('at_bats'),
            hits=Sum('hits'),
            runs=Sum('runs'),
            rbis=Sum('rbis'),
            home_runs=Sum('home_runs'),
            base_on_balls=Sum('base_on_balls'),
            strikeouts=Sum('strikeouts'),
            innings_pitched=Sum('innings_pitched'),
            earned_runs=Sum('earned_runs'),
        )

        ab = stats['at_bats'] or 0
        hits = stats['hits'] or 0
        bb = stats['base_on_balls'] or 0
        slg = hits
        obp = (hits + bb) / (ab + bb) if (ab + bb) > 0 else 0
        avg = hits / ab if ab > 0 else 0
        ops = obp + slg
        era = (stats['earned_runs'] or 0) * 9 / (stats['innings_pitched'] or 1)

        team_stats.append({
            'team': team,
            'games_played': stats['games_played'] or 0,
            'at_bats': ab,
            'hits': hits,
            'runs': stats['runs'] or 0,
            'rbis': stats['rbis'] or 0,
            'home_runs': stats['home_runs'] or 0,
            'base_on_balls': bb,
            'strikeouts': stats['strikeouts'] or 0,
            'avg': f"{avg:.3f}",
            'obp': f"{obp:.3f}",
            'slg': f"{slg:.3f}",
            'ops': f"{ops:.3f}",
            'era': f"{era:.2f}",
        })

    # === Overall Stats ===
    overall_stats_qs = PlayerGameStat.objects.filter(
        player=player,
        game__team_home__in=player_division_teams
    ) | PlayerGameStat.objects.filter(
        player=player,
        game__team_away__in=player_division_teams
    )

    overall = overall_stats_qs.aggregate(
        games_played=Count('game', distinct=True),
        at_bats=Sum('at_bats'),
        hits=Sum('hits'),
        runs=Sum('runs'),
        rbis=Sum('rbis'),
        home_runs=Sum('home_runs'),
        base_on_balls=Sum('base_on_balls'),
        strikeouts=Sum('strikeouts'),
        innings_pitched=Sum('innings_pitched'),
        earned_runs=Sum('earned_runs'),
    )

    ab = overall['at_bats'] or 0
    hits = overall['hits'] or 0
    bb = overall['base_on_balls'] or 0
    slg = hits
    obp = (hits + bb) / (ab + bb) if (ab + bb) > 0 else 0
    avg = hits / ab if ab > 0 else 0
    ops = obp + slg
    era = (overall['earned_runs'] or 0) * 9 / (overall['innings_pitched'] or 1)

    overall_stats = {
        'games_played': overall['games_played'] or 0,
        'at_bats': ab,
        'hits': hits,
        'runs': overall['runs'] or 0,
        'rbis': overall['rbis'] or 0,
        'home_runs': overall['home_runs'] or 0,
        'base_on_balls': bb,
        'strikeouts': overall['strikeouts'] or 0,
        'avg': f"{avg:.3f}",
        'obp': f"{obp:.3f}",
        'slg': f"{slg:.3f}",
        'ops': f"{ops:.3f}",
        'era': f"{era:.2f}",
    }

    return render(request, "league/player_detail.html", {
        "player": player,
        "is_coach": is_coach,
        "is_coordinator": is_coordinator,
        "player_logs": player_logs,
        "team_stats": team_stats,
        "overall_stats": overall_stats,
    })

@login_required
def dashboard(request, division_id=None):
    user = request.user

    # If user is a player
    if hasattr(user, 'player_profile'):
        return redirect('player_dashboard')

    # If user is a coordinator
    is_coordinator = Division.objects.filter(coordinators=user).exists()
    is_coach = user.teams.exists()

    # If user is only a coach and not a coordinator, redirect to coach dashboard
    if is_coach and not is_coordinator and not division_id:
        return redirect('coach_dashboard')
    # Get divisions the user can access
    coach_divisions = Division.objects.filter(teams__coaches=user).distinct()
    coordinator_divisions = Division.objects.filter(coordinators=user).distinct()
    divisions = coach_divisions | coordinator_divisions  # Union of accessible divisions

    # Handle division selection
    if division_id:
        division = get_object_or_404(Division, id=division_id)
        if division not in divisions:
            return render(request, 'league/error.html', {'message': 'You do not have access to this division.', 'divisions': divisions})
    else:
        division = coach_divisions.first()  # Try coach division first
        if not division:
            division = coordinator_divisions.first()  # Then coordinator division
        if not division:
            return render(request, 'league/no_division.html', {'divisions': divisions})

    teams = Team.objects.filter(division=division).prefetch_related('players', 'coaches')

    # Sorting for Available Players
    sort_by = request.GET.get('sort_by', 'last_name')
    sort_order = request.GET.get('sort_order', 'asc')
    order_prefix = '-' if sort_order == 'desc' else ''
    valid_sort_fields = ['first_name', 'last_name', 'rating']
    if sort_by not in valid_sort_fields:
        sort_by = 'last_name'
    
    available_players = Player.objects.filter(
        division=division, team__isnull=True, teams__isnull=True
    ).order_by(f"{order_prefix}{sort_by}")

    draft_picks = DraftPick.objects.filter(division=division)
    is_coach = Team.objects.filter(coaches=user, division=division).exists()
    is_coordinator = division.coordinators.filter(id=user.id).exists()

    # Handle POST actions
    if request.method == 'POST':
        if 'undraft_player_id' in request.POST:
            if not (is_coordinator or is_coach):
                return render(request, 'league/no_permission.html')
            
            player_id = request.POST.get('undraft_player_id')
            player = get_object_or_404(Player, id=player_id, division=division)
            
            if player.team or player.teams.exists():  # Player is drafted if either field is set
                # For coaches, check if they coach any of the player's teams
                if is_coach and not is_coordinator:
                    can_undraft = False
                    if player.team and user in player.team.coaches.all():
                        can_undraft = True
                    elif player.teams.exists():
                        for team in player.teams.all():
                            if user in team.coaches.all():
                                can_undraft = True
                                break
                    if not can_undraft:
                        return render(request, 'league/no_permission.html')
                
                # Undraft: clear both team and teams
                DraftPick.objects.filter(player=player, division=division).delete()
                player.team = None
                player.teams.clear()
                player.draft_round = None
                player.save()
            return redirect('dashboard_with_division', division_id=division.id)
        
        elif 'delete_player_id' in request.POST:
            if not is_coordinator:
                return render(request, 'league/no_permission.html')
            
            player_id = request.POST.get('delete_player_id')
            player = get_object_or_404(Player, id=player_id, division=division)
            
            if player.user:
                player.user.delete()
            else:
                player.delete()
            return redirect('dashboard_with_division', division_id=division.id)

    # Team rosters: Use teams.players, fall back to player_set for transition
    team_rosters = {}
    for team in teams:
        roster = list(team.players.all())  # Primary: ManyToMany
        if not roster:  # Fallback to ForeignKey if teams is empty
            roster = list(team.player_set.all())
        team_rosters[team.id] = roster

    return render(request, 'league/dashboard.html', {
        'division': division,
        'divisions': divisions,
        'teams': teams,
        'available_players': available_players,
        'draft_picks': draft_picks,
        'team_rosters': team_rosters,
        'is_coach': is_coach,
        'is_coordinator': is_coordinator,
        'sort_by': sort_by,
        'sort_order': sort_order,
    })

# league/views.py (relevant section)
@login_required
def make_pick(request, player_id, division_id):
    player = get_object_or_404(Player, id=player_id, division_id=division_id)
    division = get_object_or_404(Division, id=division_id)
    
    if not division.is_open:  # Check if draft is open
        return render(request, 'league/draft_closed.html', {'division': division})
    
    # Check if user is a coordinator or coach
    is_coordinator = division.coordinators.filter(id=request.user.id).exists()
    is_coach = Team.objects.filter(coaches=request.user, division=division).exists()
    
    if not (is_coordinator or is_coach):
        return render(request, 'league/no_permission.html')
    
    if request.method == 'POST':
        if is_coordinator:
            # Coordinators can select a team via POST data
            team_id = request.POST.get('team_id')
            if not team_id:
                return render(request, 'league/select_team.html', {
                    'division': division,
                    'player': player,
                    'teams': Team.objects.filter(division=division),
                })
            team = get_object_or_404(Team, id=team_id, division=division)
        else:
            # Coaches use their own team
            team = Team.objects.filter(coaches=request.user, division=division).first()
        
        if team and team.player_set.count() < team.max_players and not player.team:
            last_pick = DraftPick.objects.filter(division=division).order_by('-pick_number').first()
            pick_number = last_pick.pick_number + 1 if last_pick else 1
            round_number = (pick_number - 1) // Team.objects.filter(division=division).count() + 1
            DraftPick.objects.create(
                division=division,
                team=team,
                player=player,
                pick_number=pick_number,
                round_number=round_number
            )
            player.team = team
            player.teams.add(team)  # Add to ManyToManyField
            player.draft_round = round_number
            player.save()
            return redirect('dashboard_with_division', division_id=division_id)
    
    # If GET or team selection needed, show team selection for coordinators
    if is_coordinator:
        return render(request, 'league/select_team.html', {
            'division': division,
            'player': player,
            'teams': Team.objects.filter(division=division),
        })
    return redirect('dashboard_with_division', division_id=division_id)

@login_required
def add_player(request, division_id=None):
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            player = form.save(commit=False)
            if division_id:
                player.division = get_object_or_404(Division, id=division_id)
            player.save()
            return redirect('dashboard_with_division', division_id=division_id if division_id else None)
    else:
        form = PlayerForm()
    return render(request, 'league/add_player.html', {'form': form, 'division_id': division_id})

@login_required
def player_profile(request):
    if not hasattr(request.user, 'player_profile'):
        return redirect('dashboard')  # Redirect non-players to dashboard
    
    player = request.user.player_profile
    
    if request.method == 'POST':
        form = PlayerProfileForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            return redirect('player_profile')
    else:
        form = PlayerProfileForm(instance=player)
    
    return render(request, 'league/player_profile.html', {
        'player': player,
        'form': form,
    })


import logging

logger = logging.getLogger(__name__)

def send_activation_email(user, activation_link):
    try:
        logger.info(f"📨 Preparing to send activation email to {user.email}")
        subject = 'Activate Your Web3SportsDraft Account'
        message = render_to_string('registration/activation_email.html', {
            'user': user,
            'activation_link': activation_link,
        })
        email = EmailMessage(subject, message, to=[user.email])
        email.send()
        logger.info(f"✅ Activation email sent to: {user.email}")
    except Exception as e:
        logger.error(f"❌ Failed to send email to {user.email}: {str(e)}")


def player_signup(request):
    if request.method == 'POST':
        form = PlayerSignupForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = True # # Immediately activate
                user.email = form.cleaned_data['email']  # 🔁 Add this line
                user.save()

                Player.objects.create(
                    user=user,
                    first_name=user.first_name,
                    last_name=user.last_name,
                )

                # To use email activation, set user.is_active = False above, and uncomment the lines below
                # Build activation link
                #uid = urlsafe_base64_encode(force_bytes(user.pk))
                #token = default_token_generator.make_token(user)
                #domain = get_current_site(request).domain
                #activation_link = f"https://{domain}/activate/{uid}/{token}/"

                #Thread(target=send_activation_email, args=(user, activation_link)).start()

                #return render(request, 'registration/signup_pending.html', {'email': user.email})
                return render(request, 'registration/activation_success.html', {'email': user.email})
            except Exception as e:
                logger.exception("❌ Error during signup")
                return render(request, 'registration/signup_error.html', {'error': str(e)})
    else:
        form = PlayerSignupForm()

    return render(request, 'league/signup.html', {'form': form})

@login_required
def coach_comment(request, player_id, division_id):
    player = get_object_or_404(Player, id=player_id, division_id=division_id)
    division = get_object_or_404(Division, id=division_id)
    if not Team.objects.filter(coaches=request.user, division=division).exists():
        return render(request, 'league/no_permission.html')
    
    if request.method == 'POST':
        form = CoachCommentForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            return redirect('dashboard_with_division', division_id=division_id)
    else:
        form = CoachCommentForm(instance=player)
    
    context = {
        'form': form,
        'player': player,
    }
    return render(request, 'league/coach_comment.html', context)

# league/views.py
def public_draft(request, division_id=None):
    if division_id:
        division = get_object_or_404(Division, id=division_id)
    else:
        division = Division.objects.first()
        if not division:
            return render(request, 'league/no_division.html', {'divisions': Division.objects.all()})
    
    teams = Team.objects.filter(division=division).prefetch_related('player_set', 'coaches')
    team_rosters = {team.id: list(team.player_set.all()) for team in teams}
    draft_picks = DraftPick.objects.filter(division=division)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        draft_picks_data = [
            {
                'id': pick.id,  # Added for potential future use
                'round_number': pick.round_number if pick.round_number != 999 else 'Trade',
                'pick_number': pick.pick_number,
                'team_name': pick.team.name,
                'player_name': f"{pick.player.first_name} {pick.player.last_name}"
            }
            for pick in draft_picks
        ]
        return JsonResponse({
            'draft_picks': draft_picks_data,
            'last_updated': datetime.now().isoformat()
        })

    context = {
        'division': division,
        'draft_picks': draft_picks,
        'divisions': Division.objects.all(),
        'teams': teams,
        'team_rosters': team_rosters,
    }
    return render(request, 'league/public_draft.html', context)

# league/views.py
@login_required
def toggle_draft_status(request, division_id):
    division = get_object_or_404(Division, id=division_id)
    # Check if user is a coordinator
    if not division.coordinators.filter(id=request.user.id).exists():
        return render(request, 'league/no_permission.html')
    
    if request.method == 'POST':
        division.is_open = not division.is_open  # Toggle status
        division.save()
        return redirect('dashboard_with_division', division_id=division_id)
    
    context = {
        'division': division,
    }
    return render(request, 'league/toggle_draft.html', context)

# league/views.py
@login_required
def trade_players(request, division_id):
    division = get_object_or_404(Division, id=division_id)
    
    # Restrict to coordinators only
    if not division.coordinators.filter(id=request.user.id).exists():
        return render(request, 'league/no_permission.html')
    
    teams = Team.objects.filter(division=division)
    
    if request.method == 'POST':
        player1_id = request.POST.get('player1_id')
        player2_id = request.POST.get('player2_id', None)  # Optional for 1-for-1 or 1-for-none trades
        
        player1 = get_object_or_404(Player, id=player1_id, division=division)
        player2 = Player.objects.filter(id=player2_id, division=division).first() if player2_id else None
        
        # Validate teams and roster limits
        team1 = player1.team
        if not team1 or team1.division != division:
            return render(request, 'league/trade_error.html', {'message': 'Player 1 is not on a team in this division.'})
        
        team2 = player2.team if player2 else None
        if player2 and (not team2 or team2.division != division):
            return render(request, 'league/trade_error.html', {'message': 'Player 2 is not on a team in this division.'})
        
        # Check roster limits after trade
        if team2 and team2.player_set.count() >= team2.max_players:
            return render(request, 'league/trade_error.html', {'message': f'{team2.name} is already at max roster size.'})
        if team1 and player2 and team1.player_set.count() >= team1.max_players:
            return render(request, 'league/trade_error.html', {'message': f'{team1.name} is already at max roster size.'})
        
        # Execute the trade
        last_pick = DraftPick.objects.filter(division=division).order_by('-pick_number').first()
        pick_number = last_pick.pick_number + 1 if last_pick else 1
        
        # Trade Player 1 to Team 2 (if Team 2 exists)
        if team2:
            player1.team = team2
            player1.save()
            DraftPick.objects.create(
                division=division,
                team=team2,
                player=player1,
                pick_number=pick_number,
                round_number=999  # Special round for trades
            )
            pick_number += 1
        
        # Trade Player 2 to Team 1 (if Player 2 exists)
        if player2:
            player2.team = team1
            player2.save()
            DraftPick.objects.create(
                division=division,
                team=team1,
                player=player2,
                pick_number=pick_number,
                round_number=999  # Special round for trades
            )
        
        return redirect('dashboard_with_division', division_id=division_id)
    
    # GET request: Show trade form
    context = {
        'division': division,
        'teams': teams,
        'players': Player.objects.filter(division=division, team__isnull=False).order_by('team__name', 'last_name', 'first_name'),
    }
    return render(request, 'league/trade_players.html', context)



@login_required
def request_join_team(request):
    # Only players should access this view
    try:
        player = request.user.player_profile
    except Player.DoesNotExist:
        return render(request, "league/no_permission.html", {"message": "Only players can request to join a team."})

    if request.method == 'POST':
        form = JoinTeamRequestForm(request.POST, player=player)
        if form.is_valid():
            join_request = form.save(commit=False)
            join_request.player = player
            join_request.status = 'pending'
            join_request.save()
            return render(request, "league/join_team_pending.html", {"team": join_request.team})
    else:
        form = JoinTeamRequestForm(player=player)

    return render(request, "league/request_join_team.html", {"form": form})


@login_required
def review_join_requests(request):
    user = request.user
    teams_coached = user.teams.all()

    # Get all pending requests for teams this coach is responsible for
    pending_requests = JoinTeamRequest.objects.filter(
        team__in=teams_coached,
        status='pending'
    ).select_related('player__user', 'team')

    return render(request, 'league/review_join_requests.html', {
        "pending_requests": pending_requests,
    })


@login_required
def approve_join_request(request, request_id):
    join_request = get_object_or_404(JoinTeamRequest, id=request_id)

    # Ensure current user is a coach of the requested team
    if request.user not in join_request.team.coaches.all():
        return render(request, "league/no_permission.html", {
            "message": "You are not authorized to approve this request."
        })

    # Add player to team
    join_request.team.players.add(join_request.player)
    join_request.status = 'approved'
    join_request.save()

    messages.success(request, f"{join_request.player.first_name} has been added to {join_request.team.name}.")
    return redirect('review_join_requests')

@login_required
def find_teams(request):
    player = get_object_or_404(Player, user=request.user)

    # Teams the player is already on
    existing_team_ids = player.teams.values_list('id', flat=True)

    # Teams the player has already requested to join
    requested_team_ids = JoinTeamRequest.objects.filter(
        player=player
    ).values_list('team_id', flat=True)

    # Available teams = all teams - already on - already requested
    available_teams = Team.objects.exclude(
        Q(id__in=existing_team_ids) | Q(id__in=requested_team_ids)
    ).select_related('division')

    return render(request, 'league/find_teams.html', {
        'available_teams': available_teams,
        'player':player,
    })


@login_required
def request_join_team(request, team_id):
    player = get_object_or_404(Player, user=request.user)
    team = get_object_or_404(Team, id=team_id)

    # Check if already a member or already requested
    if player.teams.filter(id=team.id).exists() or JoinTeamRequest.objects.filter(player=player, team=team).exists():
        messages.warning(request, "You’ve already joined or requested this team.")
    else:
        JoinTeamRequest.objects.create(player=player, team=team)
        messages.success(request, f"Request to join {team.name} sent!")

    return redirect('find_teams')


from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def approve_join_request(request, request_id):
    join_request = get_object_or_404(JoinTeamRequest, id=request_id)

    # Check the current user is a coach of that team
    if request.user not in join_request.team.coaches.all():
        return render(request, 'league/no_permission.html', {"message": "You don't have permission to approve this request."})

    if request.method == 'POST':
        join_request.is_approved = True
        join_request.reviewed_at = timezone.now()
        join_request.save()

        join_request.team.players.add(join_request.player)

    return redirect('coach_dashboard')


@login_required
def reject_join_request(request, request_id):
    join_request = get_object_or_404(JoinTeamRequest, id=request_id)

    # Only allow if coach is coaching this team
    if request.user not in join_request.team.coaches.all():
        return render(request, "league/no_permission.html", {
            "message": "You are not allowed to reject this request."
        })

    join_request.is_approved = False
    join_request.reviewed_at = timezone.now()
    join_request.save()
    return redirect('coach_dashboard')  # or wherever you want to redirect after

@login_required
def cancel_join_request(request, request_id):
    join_request = get_object_or_404(JoinTeamRequest, id=request_id, player=request.user.player_profile)

    if join_request.is_approved is None:
        join_request.delete()
        messages.success(request, f"Cancelled join request to {join_request.team.name}.")
    else:
        messages.warning(request, "You can only cancel a pending request.")
    
    return redirect('find_teams')

@login_required
def re_request_join_team(request, team_id):
    player = request.user.player_profile
    team = get_object_or_404(Team, id=team_id)

    # Delete the previous rejected request
    JoinTeamRequest.objects.filter(team=team, player=player, is_approved=False).delete()

    # Create a new pending request
    JoinTeamRequest.objects.create(team=team, player=player)
    messages.success(request, f"Re-requested to join {team.name}.")

    return redirect('player_dashboard')



@login_required
def delete_join_request(request, request_id):
    join_request = get_object_or_404(JoinTeamRequest, id=request_id, player=request.user.player_profile)
    if request.method == 'POST':
        join_request.delete()
    return redirect('player_dashboard')

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Prevents logout after password change
            messages.success(request, '✅ Your password was successfully updated!')
            #return redirect('player_dashboard')  # Or any other page you want
            return redirect('dashboard')  # Or any other page you want
        else:
            messages.error(request, '⚠️ Please correct the error below.')
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'league/custom_change_password.html', {'form': form})

@staff_member_required
def signin_log_view(request):
    logs = SignInLog.objects.select_related('user').order_by('-timestamp')[:100]  # Show latest 100
    return render(request, 'league/signin_log.html', {'logs': logs})


#############################################
# Self-submitting game stats and coach review
#############################################
@login_required
def submit_stats(request):
    if request.method == 'POST':
        form = PlayerGameStatForm(request.POST)
        if form.is_valid():
            stat = form.save(commit=False)
            stat.player = request.user.player
            stat.submitted_by = request.user
            stat.source = 'self'
            stat.is_verified = False
            stat.save()
            return redirect('player_dashboard')
    else:
        form = PlayerGameStatForm()
    return render(request, 'league/submit_stats.html', {'form': form})

@login_required
def review_stats(request):
    if not request.user.is_coach:
        return HttpResponseForbidden()
    pending_stats = PlayerGameStat.objects.filter(is_verified=False, source='self')
    return render(request, 'league/review_stats.html', {'pending_stats': pending_stats})

@login_required
def verify_stat(request, stat_id):
    stat = get_object_or_404(PlayerGameStat, id=stat_id)
    if request.method == 'POST':
        stat.is_verified = True
        stat.save()
        return redirect('review_stats')




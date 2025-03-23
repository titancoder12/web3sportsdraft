# league/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse  # Ensure this line is present
from .models import Team, Player, DraftPick, Division, PlayerGameStat, Game
from django.contrib.auth.decorators import login_required
from .forms import PlayerForm, PlayerProfileForm, PlayerSignupForm, CoachCommentForm, PlayerCSVUploadForm
from django.contrib.auth.models import User
import csv
from io import TextIOWrapper
from datetime import datetime
from django.contrib import messages
from django.shortcuts import render
from django.db.models import Sum


@login_required
def player_dashboard(request):
    user = request.user

    # Ensure the user has an associated Player
    try:
        player = user.player_profile # user.player
    except Player.DoesNotExist:
        return render(request, "league/player_dashboard.html", {"error": "No player profile found."})

    # Game history with stats
    game_stats = PlayerGameStat.objects.select_related("game").filter(player=player).order_by("-game__date")

    # Aggregate overall stats
    overall_stats = game_stats.aggregate(
        at_bats=Sum("at_bats"),
        hits=Sum("hits"),
        runs=Sum("runs"),
        rbis=Sum("rbis"),
        home_runs=Sum("home_runs"),
        strikeouts=Sum("strikeouts"),
        base_on_balls=Sum("base_on_balls"),
    )

    return render(request, "league/player_dashboard.html", {
        "player": player,
        "game_stats": game_stats,
        "overall_stats": overall_stats,
    })

def box_score_view(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    home_team_stats = PlayerGameStat.objects.filter(game=game, player__teams=game.team_home)
    away_team_stats = PlayerGameStat.objects.filter(game=game, player__teams=game.team_away)

    context = {
        'game': game,
        'home_team_stats': home_team_stats,
        'away_team_stats': away_team_stats,
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
    player = get_object_or_404(Player, id=player_id)
    return render(request, 'league/player_detail.html', {'player': player})

@login_required
def dashboard(request, division_id=None):
    if hasattr(request.user, 'player_profile'):
        return redirect('player_profile')

    user = request.user

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

# league/views.py (relevant section)
def signup(request):
    if request.method == 'POST':
        form = PlayerSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('player_profile')
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


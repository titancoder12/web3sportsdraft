# league/views.py
# league/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Team, Player, DraftPick, Division
from .forms import PlayerForm, PlayerProfileForm, PlayerSignupForm, CoachCommentForm

@login_required
def dashboard(request, division_id=None):
    if hasattr(request.user, 'player_profile'):
        return redirect('player_profile')
    
    if division_id:
        division = get_object_or_404(Division, id=division_id)
    else:
        division = Division.objects.filter(teams__coaches=request.user).first()
        if not division:
            division = Division.objects.filter(coordinators=request.user).first()
        if not division:
            return render(request, 'league/no_division.html', {'divisions': Division.objects.all()})
    
    teams = Team.objects.filter(division=division).prefetch_related('player_set', 'coaches')
    available_players = Player.objects.filter(division=division, team__isnull=True)
    draft_picks = DraftPick.objects.filter(division=division)
    is_coach = Team.objects.filter(coaches=request.user, division=division).exists()
    is_coordinator = division.coordinators.filter(id=request.user.id).exists()

    # Handle undraft action
    if request.method == 'POST' and 'undraft_player_id' in request.POST:
        if not (is_coordinator or is_coach):  # Restrict to coordinators or coaches
            return render(request, 'league/no_permission.html')
        
        player_id = request.POST.get('undraft_player_id')
        player = get_object_or_404(Player, id=player_id, division=division)
        
        # Only allow undrafting if the player is on a team
        if player.team:
            # Optionally restrict coaches to their own team
            if is_coach and not is_coordinator and not player.team.coaches.filter(id=request.user.id).exists():
                return render(request, 'league/no_permission.html')
            
            # Remove player from team and delete related DraftPick
            DraftPick.objects.filter(player=player, division=division).delete()
            player.team = None
            player.draft_round = None
            player.save()
        return redirect('dashboard_with_division', division_id=division_id)

    # Prepare team rosters
    team_rosters = {team.id: list(team.player_set.all()) for team in teams}

    context = {
        'division': division,
        'teams': teams,
        'players': available_players,
        'draft_picks': draft_picks,
        'is_coach': is_coach,
        'is_coordinator': is_coordinator,
        'divisions': Division.objects.all(),
        'team_rosters': team_rosters,
    }
    return render(request, 'league/dashboard.html', context)

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
    try:
        player = request.user.player_profile
    except Player.DoesNotExist:
        return render(request, 'league/no_profile.html')
    
    if request.method == 'POST':
        form = PlayerProfileForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            return redirect('player_profile')
    else:
        form = PlayerProfileForm(instance=player)
    
    context = {
        'form': form,
        'player': player,
    }
    return render(request, 'league/player_profile.html', context)

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

def public_draft(request, division_id=None):
    if division_id:
        division = get_object_or_404(Division, id=division_id)
    else:
        division = Division.objects.first()
        if not division:
            return render(request, 'league/no_division.html', {'divisions': Division.objects.all()})
    
    draft_picks = DraftPick.objects.filter(division=division)
    teams = Team.objects.filter(division=division).prefetch_related('player_set', 'coaches')  # Optimize queries
    team_rosters = {team.id: list(team.player_set.all()) for team in teams}

    context = {
        'division': division,
        'draft_picks': draft_picks,
        'divisions': Division.objects.all(),
        'teams': teams,
        'team_rosters': team_rosters,  # New context variable
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
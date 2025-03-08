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
            return render(request, 'league/no_division.html')
    
    teams = Team.objects.filter(division=division)
    available_players = Player.objects.filter(division=division, team__isnull=True)  # Scope to division
    draft_picks = DraftPick.objects.filter(division=division)
    is_coach = Team.objects.filter(coaches=request.user, division=division).exists()
    divisions = Division.objects.all()

    context = {
        'division': division,
        'teams': teams,
        'players': available_players,
        'draft_picks': draft_picks,
        'is_coach': is_coach,
        'divisions': divisions,
    }
    return render(request, 'league/dashboard.html', context)

# league/views.py (relevant section)
@login_required
def make_pick(request, player_id, division_id):
    if request.method == 'POST':
        player = get_object_or_404(Player, id=player_id, division_id=division_id)
        division = get_object_or_404(Division, id=division_id)
        
        if not division.is_open:  # Check if draft is open
            return render(request, 'league/draft_closed.html', {'division': division})
        
        try:
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
        except Team.DoesNotExist:
            pass
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
        draft_picks = DraftPick.objects.filter(division=division)
    else:
        draft_picks = DraftPick.objects.all()  # Show all if no division specified
        division = None
    
    context = {
        'division': division,
        'draft_picks': draft_picks,
        'divisions': Division.objects.all(),  # For navigation
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
# league/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Team, Player, DraftPick
from .forms import PlayerForm, PlayerProfileForm, PlayerSignupForm, CoachCommentForm

@login_required
def dashboard(request):
    if hasattr(request.user, 'player_profile'):
        return redirect('player_profile')
    
    teams = Team.objects.all()
    available_players = Player.objects.filter(team__isnull=True)
    draft_picks = DraftPick.objects.all()
    is_coach = Team.objects.filter(coaches=request.user).exists()

    context = {
        'teams': teams,
        'players': available_players,
        'draft_picks': draft_picks,
        'is_coach': is_coach,
    }
    return render(request, 'league/dashboard.html', context)

@login_required
def make_pick(request, player_id):
    if request.method == 'POST':
        player = Player.objects.get(id=player_id)
        try:
            team = Team.objects.filter(coaches=request.user).first()
            if team and team.player_set.count() < team.max_players and not player.team:
                last_pick = DraftPick.objects.order_by('-pick_number').first()
                pick_number = last_pick.pick_number + 1 if last_pick else 1
                round_number = (pick_number - 1) // Team.objects.count() + 1
                DraftPick.objects.create(
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
    return redirect('dashboard')

@login_required
def add_player(request):
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = PlayerForm()
    return render(request, 'league/add_player.html', {'form': form})

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
def coach_comment(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    if not Team.objects.filter(coaches=request.user).exists():
        return render(request, 'league/no_permission.html')
    
    if request.method == 'POST':
        form = CoachCommentForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = CoachCommentForm(instance=player)
    
    context = {
        'form': form,
        'player': player,
    }
    return render(request, 'league/coach_comment.html', context)

def public_draft(request):
    draft_picks = DraftPick.objects.all()
    context = {
        'draft_picks': draft_picks,
    }
    return render(request, 'league/public_draft.html', context)
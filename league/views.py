# league/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Team, Player, DraftPick
from .forms import PlayerForm

@login_required
def dashboard(request):
    teams = Team.objects.all()
    available_players = Player.objects.filter(team__isnull=True)
    draft_picks = DraftPick.objects.all()
    context = {
        'teams': teams,
        'players': available_players,
        'draft_picks': draft_picks,
    }
    return render(request, 'league/dashboard.html', context)

@login_required
def make_pick(request, player_id):
    if request.method == 'POST':
        player = Player.objects.get(id=player_id)
        try:
            # Get the first team where the user is a coach
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
            pass  # User isn't a coach of any team
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
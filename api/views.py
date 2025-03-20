from django.shortcuts import render
from rest_framework import viewsets
from .serializers import *
from league.models import *
from .serializers import *
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import csv
import io
from datetime import datetime
import uuid  # To generate unique game IDs
from rest_framework.authentication import TokenAuthentication


@api_view(['POST'])
@authentication_classes([TokenAuthentication]) 
@permission_classes([IsAuthenticated])
def upload_box_score(request):
    """
    Allows coaches to upload a box score in CSV format using the player's username.
    If no game_id is provided, a new Game is created automatically.
    """
    if 'file' not in request.FILES:
        return Response({"error": "CSV file required."}, status=400)

    csv_file = request.FILES['file']
    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)  # Skip header row

    created_games = {}  # Store new games to avoid duplicate creation

    for row in csv.reader(io_string, delimiter=','):
        (
            game_id, username, at_bats, runs, hits, rbis, singles, doubles, triples, home_runs,
            strikeouts, base_on_balls, hit_by_pitch, sacrifice_flies, innings_pitched, hits_allowed,
            runs_allowed, earned_runs, walks_allowed, strikeouts_pitching, home_runs_allowed,
            team_home, team_away, date, time, location
        ) = row

        # Auto-create Game if game_id is missing
        if not game_id:
            game_id = str(uuid.uuid4())  # Generate a unique game_id
            if game_id not in created_games:
                game = Game.objects.create(
                    game_id=game_id,
                    team_home=Team.objects.get_or_create(name=team_home)[0],
                    team_away=Team.objects.get_or_create(name=team_away)[0],
                    date=datetime.strptime(date, "%Y-%m-%d"),
                    time=datetime.strptime(time, "%H:%M").time(),
                    location=location,
                    finalized=False,
                    is_verified=False,
                )
                created_games[game_id] = game
            else:
                game = created_games[game_id]
        else:
            try:
                game = Game.objects.get(game_id=game_id)
            except Game.DoesNotExist:
                return Response({"error": f"Game with ID {game_id} not found."}, status=404)

        try:
            player = Player.objects.get(user__username=username)  # Query by username
            stat, created = PlayerGameStat.objects.get_or_create(player=player, game=game)

            # Hitting Stats
            stat.at_bats = int(at_bats)
            stat.runs = int(runs)
            stat.hits = int(hits)
            stat.rbis = int(rbis)
            stat.singles = int(singles)
            stat.doubles = int(doubles)
            stat.triples = int(triples)
            stat.home_runs = int(home_runs)
            stat.strikeouts = int(strikeouts)
            stat.base_on_balls = int(base_on_balls)
            stat.hit_by_pitch = int(hit_by_pitch)
            stat.sacrifice_flies = int(sacrifice_flies)

            # Pitching Stats
            stat.innings_pitched = float(innings_pitched)
            stat.hits_allowed = int(hits_allowed)
            stat.runs_allowed = int(runs_allowed)
            stat.earned_runs = int(earned_runs)
            stat.walks_allowed = int(walks_allowed)
            stat.strikeouts_pitching = int(strikeouts_pitching)
            stat.home_runs_allowed = int(home_runs_allowed)

            stat.is_verified = False  # Awaiting coach approval
            stat.save()

        except Player.DoesNotExist:
            continue  # Skip entries where the player does not exist

    return Response({"message": "Box score uploaded successfully. Awaiting verification."}, status=201)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication]) 
def verify_player_stats(request, stat_id):
    """
    Allows a coach to verify a player's submitted stats.
    """
    try:
        stat = PlayerGameStat.objects.get(id=stat_id)
        stat.is_verified = True
        stat.save()
        return Response({"message": "Player stats verified successfully."}, status=200)
    except PlayerGameStat.DoesNotExist:
        return Response({"error": "Player stats not found."}, status=404)


# Create your views here.
class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [permissions.IsAuthenticated]

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]

class DivisionViewSet(viewsets.ModelViewSet):
    queryset = Division.objects.all()
    serializer_class = DivisionSerializer
    permission_classes = [permissions.IsAuthenticated]

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [permissions.IsAuthenticated]

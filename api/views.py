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
    Imports box score data. Uses `team_id` and `is_home`. Supports separate or combined uploads.
    Allows player details (first/last name) to be included for readability.
    """

    if 'file' not in request.FILES:
        return Response({"error": "CSV file required."}, status=400)

    csv_file = request.FILES['file']
    try:
        data_set = csv_file.read().decode('UTF-8')
    except UnicodeDecodeError:
        return Response({"error": "Invalid file encoding. Please upload a UTF-8 encoded CSV file."}, status=400)

    io_string = io.StringIO(data_set)
    headers = next(io_string)  # Skip header row

    created_game = None
    error_rows = []

    for index, row in enumerate(csv.reader(io_string, delimiter=','), start=2):
        try:
            (
                game_id, first_name, last_name, username, at_bats, runs, hits, rbis, singles, doubles,
                triples, home_runs, strikeouts, base_on_balls, hit_by_pitch, sacrifice_flies,
                innings_pitched, hits_allowed, runs_allowed, earned_runs, walks_allowed,
                strikeouts_pitching, home_runs_allowed, team_id, is_home, date, time, location
            ) = row

            # Get team
            try:
                team = Team.objects.get(id=int(team_id))
            except Team.DoesNotExist:
                error_rows.append(f"Row {index}: Team ID '{team_id}' not found.")
                continue

            is_home = is_home.lower() == "true"

            # Game lookup or creation
            if game_id:
                game = Game.objects.filter(game_id=game_id).first()
                if not game:
                    error_rows.append(f"Row {index}: Game ID '{game_id}' not found.")
                    continue

                if is_home and not game.team_home:
                    game.team_home = team
                elif not is_home and not game.team_away:
                    game.team_away = team
                game.save()
            else:
                if created_game is None:
                    game = Game.objects.create(
                        game_id=str(uuid.uuid4()),
                        team_home=team if is_home else None,
                        team_away=team if not is_home else None,
                        date=datetime.strptime(date, "%Y-%m-%d"),
                        time=datetime.strptime(time, "%H:%M").time(),
                        location=location,
                        finalized=False,
                        is_verified=False,
                    )
                    created_game = game
                else:
                    game = created_game

            # Get player by username
            player = Player.objects.filter(user__username=username).first()
            if not player:
                error_rows.append(f"Row {index}: Player '{first_name} {last_name}' (username: '{username}') not found.")
                continue

            stat, _ = PlayerGameStat.objects.get_or_create(player=player, game=game)

            # Hitting
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

            # Pitching
            stat.innings_pitched = float(innings_pitched)
            stat.hits_allowed = int(hits_allowed)
            stat.runs_allowed = int(runs_allowed)
            stat.earned_runs = int(earned_runs)
            stat.walks_allowed = int(walks_allowed)
            stat.strikeouts_pitching = int(strikeouts_pitching)
            stat.home_runs_allowed = int(home_runs_allowed)

            stat.is_verified = True
            stat.save()

        except ValueError as e:
            error_rows.append(f"Row {index}: Data format error - {str(e)}")

    response = {"message": "Box score upload complete."}
    if error_rows:
        response["warnings"] = error_rows
        return Response(response, status=207)
    return Response(response, status=201)

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

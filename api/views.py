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
    If `game_id` is not specified, all rows without `game_id` belong to a single newly created game.
    Rows with `game_id` are linked to existing games (or skipped if the game does not exist).
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

    # Initialize variables
    created_game = None  # Only create one game for rows without `game_id`
    error_rows = []  # Track problematic rows

    for index, row in enumerate(csv.reader(io_string, delimiter=','), start=2):  # Start=2 to account for the header row
        try:
            (
                game_id, username, at_bats, runs, hits, rbis, singles, doubles, triples, home_runs,
                strikeouts, base_on_balls, hit_by_pitch, sacrifice_flies, innings_pitched, hits_allowed,
                runs_allowed, earned_runs, walks_allowed, strikeouts_pitching, home_runs_allowed,
                team_home, team_away, date, time, location
            ) = row

            # If `game_id` is provided, link to the existing game
            if game_id:
                game = Game.objects.filter(game_id=game_id).first()
                if not game:
                    error_rows.append(f"Row {index}: Game with ID '{game_id}' not found.")
                    continue  # Skip this row

            # If `game_id` is NOT provided, ensure all such rows belong to the same new game
            else:
                if created_game is None:  # Create the new game only once
                    home_team_obj, _ = Team.objects.get_or_create(name=team_home)
                    away_team_obj, _ = Team.objects.get_or_create(name=team_away)

                    created_game = Game.objects.create(
                        game_id=str(uuid.uuid4()),  # Generate unique game_id
                        team_home=home_team_obj,
                        team_away=away_team_obj,
                        date=datetime.strptime(date, "%Y-%m-%d"),
                        time=datetime.strptime(time, "%H:%M").time(),
                        location=location,
                        finalized=False,
                        is_verified=False,
                    )

                game = created_game  # Assign the newly created game

            # Validate player existence
            player = Player.objects.filter(user__username=username).first()
            if not player:
                error_rows.append(f"Row {index}: Player with username '{username}' not found.")
                continue  # Skip this row

            # Create or update the player's stats
            stat, created = PlayerGameStat.objects.get_or_create(player=player, game=game)

            # Update Hitting Stats
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

            # Update Pitching Stats
            stat.innings_pitched = float(innings_pitched)
            stat.hits_allowed = int(hits_allowed)
            stat.runs_allowed = int(runs_allowed)
            stat.earned_runs = int(earned_runs)
            stat.walks_allowed = int(walks_allowed)
            stat.strikeouts_pitching = int(strikeouts_pitching)
            stat.home_runs_allowed = int(home_runs_allowed)

            stat.is_verified = True # Import stats are automatically verified
            stat.save()

        except ValueError as e:
            error_rows.append(f"Row {index}: Data format error - {str(e)}")

    response_message = {"message": "Box score uploaded successfully. Awaiting verification."}
    if error_rows:
        response_message["warnings"] = error_rows

    return Response(response_message, status=201 if not error_rows else 207)

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

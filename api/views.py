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
from django.utils.timezone import make_aware

@api_view(['POST'])
@authentication_classes([TokenAuthentication]) 
@permission_classes([IsAuthenticated])
def upload_box_score(request):
    if 'file' not in request.FILES:
        return Response({"error": "CSV file required."}, status=400)

    csv_file = request.FILES['file']
    try:
        data_set = csv_file.read().decode('UTF-8')
    except UnicodeDecodeError:
        return Response({"error": "Invalid file encoding. Please upload a UTF-8 encoded CSV file."}, status=400)

    io_string = io.StringIO(data_set)
    headers = next(io_string)  # Skip CSV header row

    error_rows = []
    game_data_cache = {}

    # For optional memory of missing date/time/location
    last_date_str = ""
    last_time_str = ""
    last_location = ""

    def process_stat_row(row_data, game, index):
        (
            game_id, first_name, last_name, username, at_bats, runs, hits, rbis, singles, doubles,
            triples, home_runs, strikeouts, base_on_balls, hit_by_pitch, sacrifice_flies,
            innings_pitched, hits_allowed, runs_allowed, earned_runs, walks_allowed,
            strikeouts_pitching, home_runs_allowed, team_id, is_home, *_  # ignore trailing values
        ) = row_data

        player = Player.objects.filter(user__username=username).first()
        if not player:
            error_rows.append(f"Row {index}: Player '{first_name} {last_name}' (username: '{username}') not found.")
            return

        stat, _ = PlayerGameStat.objects.get_or_create(player=player, game=game)

        # Set all stat fields
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

        stat.innings_pitched = float(innings_pitched)
        stat.hits_allowed = int(hits_allowed)
        stat.runs_allowed = int(runs_allowed)
        stat.earned_runs = int(earned_runs)
        stat.walks_allowed = int(walks_allowed)
        stat.strikeouts_pitching = int(strikeouts_pitching)
        stat.home_runs_allowed = int(home_runs_allowed)

        stat.is_verified = True
        stat.save()

    for index, row in enumerate(csv.reader(io_string, delimiter=','), start=2):
        try:
            (
                game_id, first_name, last_name, username, at_bats, runs, hits, rbis, singles, doubles,
                triples, home_runs, strikeouts, base_on_balls, hit_by_pitch, sacrifice_flies,
                innings_pitched, hits_allowed, runs_allowed, earned_runs, walks_allowed,
                strikeouts_pitching, home_runs_allowed, team_id, is_home, date_str, time_str, location
            ) = row

            try:
                team = Team.objects.get(id=int(team_id))
            except Team.DoesNotExist:
                error_rows.append(f"Row {index}: Team ID '{team_id}' not found.")
                continue

            is_home = is_home.lower() == "true"

            # Track last-known date/time/location
            if date_str.strip():
                last_date_str = date_str
            if time_str.strip():
                last_time_str = time_str
            if location.strip():
                last_location = location

            date_str = last_date_str
            time_str = last_time_str
            location = last_location

            if not date_str or not time_str or not location:
                error_rows.append(f"Row {index}: Missing date/time/location.")
                continue

            # If game_id is provided, use it
            if game_id:
                game = Game.objects.filter(game_id=game_id).first()
                if not game:
                    error_rows.append(f"Row {index}: Game ID '{game_id}' not found.")
                    continue
                process_stat_row(row, game, index)
                continue

            # No game_id, group by date-time-location
            key = f"{date_str}_{time_str}_{location}"
            if key not in game_data_cache:
                game_data_cache[key] = {
                    "home_team": None,
                    "away_team": None,
                    "date": make_aware(datetime.strptime(date_str, "%Y-%m-%d")),
                    "time": datetime.strptime(time_str, "%H:%M").time(),
                    "location": location,
                    "game": None,
                    "buffered_rows": [],
                }

            entry = game_data_cache[key]

            # Assign team
            if is_home:
                entry["home_team"] = team
            else:
                entry["away_team"] = team

            # If game exists now, process this stat row immediately
            if (entry["home_team"] or entry["away_team"]) and entry["game"] is None:
                entry["game"] = Game.objects.create(
                    game_id=str(uuid.uuid4()),
                    date=entry["date"],
                    time=entry["time"],
                    location=entry["location"],
                    team_home=entry["home_team"],
                    team_away=entry["away_team"],
                    finalized=False,
                    is_verified=False,
                )

                # Process any rows that were buffered
                for buffered_row, buffered_index in entry["buffered_rows"]:
                    process_stat_row(buffered_row, entry["game"], buffered_index)
                entry["buffered_rows"] = []

            if entry["game"]:
                process_stat_row(row, entry["game"], index)
            else:
                entry["buffered_rows"].append((row, index))

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


class PlayerGameStatViewSet(viewsets.ModelViewSet):
    queryset = PlayerGameStat.objects.all()
    serializer_class = PlayerGameStatSerializer
    permission_classes = [permissions.IsAuthenticated]

class LeagueViewSet(viewsets.ModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer
    permission_classes = [IsAuthenticated]

class FairPlayRuleSetViewSet(viewsets.ModelViewSet):
    queryset = FairPlayRuleSet.objects.all()
    serializer_class = FairPlayRuleSetSerializer
    permission_classes = [IsAuthenticated]

class LineupPlanViewSet(viewsets.ModelViewSet):
    queryset = LineupPlan.objects.all()
    serializer_class = LineupPlanSerializer
    permission_classes = [IsAuthenticated]

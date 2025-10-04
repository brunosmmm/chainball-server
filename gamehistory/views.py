"""Game history views."""

from .serializers import (
    TournamentSerializer,
    SeasonSerializer,
    GameSerializer,
    GameEventSerializer,
    TournamentLocationSerializer,
    TournamentCourtSerializer,
    GameAnnounceSerializer,
)
from .models import (
    TournamentCourt,
    TournamentLocation,
    Tournament,
    Season,
    Game,
    InvalidGameActionError,
    GameEvent,
    GameAnnounce,
)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey
import logging
import json

LOGGER = logging.getLogger(__name__)


class TournamentViewSet(viewsets.ReadOnlyModelViewSet):
    """Tournament viewset."""

    permission_classes = [HasAPIKey | IsAuthenticated]
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer


class TournamentLocationViewSet(viewsets.ReadOnlyModelViewSet):
    """Tournament location viewset."""

    permission_classes = [HasAPIKey | IsAuthenticated]
    queryset = TournamentLocation.objects.all()
    serializer_class = TournamentLocationSerializer


class TournamentCourtViewSet(viewsets.ReadOnlyModelViewSet):
    """Tournament court viewset."""

    permission_classes = [HasAPIKey | IsAuthenticated]
    queryset = TournamentCourt.objects.all()
    serializer_class = TournamentCourtSerializer


class SeasonViewSet(viewsets.ReadOnlyModelViewSet):
    """Season viewset."""

    permission_classes = [HasAPIKey | IsAuthenticated]
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    """Season viewset."""

    permission_classes = [HasAPIKey | IsAuthenticated]
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    @action(detail=True, methods=["post"])
    def start_game(self, request, pk=None):
        """Flag game as live."""
        LOGGER.info("Trying to flag game as started...")
        game = self.get_object()
        try:
            request_data = json.loads(request.data["payload"])
        except (KeyError, json.JSONDecodeError):
            return Response({"status": "error", "error": "malformed request"})
        try:
            game.start_game(**request_data)
        except InvalidGameActionError as ex:
            # cannot start
            LOGGER.error(f"Cannot start game: {ex}")
            return Response({"status": "error", "error": str(ex)})

        return Response({"status": "ok"})

    @action(detail=True, methods=["post"])
    def stop_game(self, request, pk=None):
        """Flag game as done."""
        game = self.get_object()
        try:
            request_data = json.loads(request.data["payload"])
        except (KeyError, json.JSONDecodeError):
            return Response({"status": "error", "error": "malformed request"})
        try:
            game.stop_game(**request_data)
        except InvalidGameActionError as ex:
            return Response({"status": "error", "error": str(ex)})

        return Response({"status": "ok"})

    @action(detail=True, methods=["post"])
    def push_event(self, request, pk=None):
        """Push event."""
        game = self.get_object()
        try:
            request_data = json.loads(request.data["payload"])
        except (KeyError, json.JSONDecodeError):
            return Response({"status": "error", "error": "malformed request"})
        try:
            game.push_event(**request_data)
        except InvalidGameActionError as ex:
            LOGGER.error(f"ERROR: Cannot push event: {ex}")
            return Response({"status": "error", "error": str(ex)})

        return Response({"status": "ok"})

    @action(detail=True)
    def undo_last_event(self, request, pk=None):
        """Undo last event."""
        game = self.get_object()
        try:
            game.undo_last_event()
        except InvalidGameActionError as ex:
            return Response({"status": "error", "error": str(ex)})

        return Response({"status": "ok"})


class GameEventViewSet(viewsets.ReadOnlyModelViewSet):
    """Game event viewset."""

    permission_classes = [HasAPIKey | IsAuthenticated]
    queryset = GameEvent.objects.all()
    serializer_class = GameEventSerializer


class AnnounceViewSet(viewsets.ModelViewSet):
    """Announce view set."""

    permission_classes = [HasAPIKey | IsAuthenticated]
    queryset = GameAnnounce.objects.all()
    serializer_class = GameAnnounceSerializer

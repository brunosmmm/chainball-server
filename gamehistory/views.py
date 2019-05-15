"""Game history views."""

from .serializers import TournamentSerializer, SeasonSerializer, GameSerializer
from .models import Tournament, Season, Game, InvalidGameActionError
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey


class TournamentViewSet(viewsets.ReadOnlyModelViewSet):
    """Tournament viewset."""

    permission_classes = [HasAPIKey | IsAuthenticated]
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer


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
        game = self.get_object()
        try:
            game.start_game(**request.data)
        except InvalidGameActionError as ex:
            # cannot start
            return Response({"status": "error", "error": ex})

        return Response({"status": "ok"})

    @action(detail=True, methods=["post"])
    def stop_game(self, request, pk=None):
        """Flag game as done."""
        game = self.get_object()
        try:
            game.stop_game(**request.data)
        except InvalidGameActionError as ex:
            return Response({"status": "error", "error": ex})

        return Response({"status": "ok"})

    @action(detail=True, methods=["post"])
    def push_event(self, request, pk=None):
        """Push event."""
        game = self.get_object()
        try:
            game.push_event(**request.data)
        except InvalidGameActionError as ex:
            return Response({"status": "error", "error": ex})

        return Response({"status": "ok"})

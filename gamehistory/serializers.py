"""Serializers for game history data."""

from rest_framework import serializers
from .models import (
    TournamentLocation,
    TournamentCourt,
    Tournament,
    Season,
    Game,
    GameEvent,
)


class SeasonSerializer(serializers.HyperlinkedModelSerializer):
    """Season serializer."""

    class Meta:
        model = Season
        fields = ("id", "year", "tournaments")


class TournamentSerializer(serializers.HyperlinkedModelSerializer):
    """Tournament serializer."""

    class Meta:
        model = Tournament
        fields = (
            "id",
            "season",
            "description",
            "event_date",
            "players",
            "status",
            "games",
            "location",
        )


class GameSerializer(serializers.HyperlinkedModelSerializer):
    """Game serializer."""

    class Meta:
        model = Game
        fields = (
            "identifier",
            "sequence",
            "description",
            "tournament",
            "events",
            "players",
            "duration",
            "start_time",
            "game_status",
            "player_order",
            "court",
            "p0_score",
            "p1_score",
            "p2_score",
            "p3_score",
        )


class GameEventSerializer(serializers.HyperlinkedModelSerializer):
    """Game Event serializer."""

    class Meta:
        model = GameEvent
        fields = ("event", "data")


class TournamentLocationSerializer(serializers.HyperlinkedModelSerializer):
    """Tournament location serializer."""

    class Meta:
        model = TournamentLocation
        fields = ("name",)


class TournamentCourtSerializer(serializers.HyperlinkedModelSerializer):
    """Tournament court serializer."""

    class Meta:
        model = TournamentCourt
        fields = ("number", "location")

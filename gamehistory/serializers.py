"""Serializers for game history data."""

from rest_framework import serializers
from .models import Tournament, Season, Game


class SeasonSerializer(serializers.HyperlinkedModelSerializer):
    """Season serializer."""

    class Meta:
        model = Season
        fields = ("year", "tournaments")


class TournamentSerializer(serializers.HyperlinkedModelSerializer):
    """Tournament serializer."""

    class Meta:
        model = Tournament
        fields = (
            "season",
            "description",
            "event_date",
            "players",
            "status",
            "games",
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
        )

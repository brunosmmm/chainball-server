"""Serializers for game history data."""

from rest_framework import serializers
from .models import Tournament


class TournamentSerializer(serializers.HyperlinkedModelSerializer):
    """Tournament serializer."""

    class Meta:
        model = Tournament
        fields = ("season", "description", "event_date", "players", "status")

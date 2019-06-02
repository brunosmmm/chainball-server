"""Serializers for player data."""

from rest_framework import serializers
from .models import Player


class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    """Player model serializer."""

    class Meta:
        model = Player
        fields = ("name", "display_name", "codename", "username", "sfx_md5")

"""Player registry views."""

from .serializers import PlayerSerializer
from .models import Player
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    """Player viewset."""

    permission_classes = [HasAPIKey | IsAuthenticated]
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

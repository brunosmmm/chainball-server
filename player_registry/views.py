"""Player registry views."""

from .serializers import PlayerSerializer
from .models import Player
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    """Player viewset."""

    permission_classes = [HasAPIKey | IsAuthenticated]
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

    @action(detail=True)
    def get_sfx_data(self, request, pk=None):
        """Get SFX data."""
        player = self.get_object()

        sfx_data = player.sfx_data_b64
        return Response({"status": "ok", "data": sfx_data})

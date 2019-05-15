"""Game history views."""

from .serializers import TournamentSerializer
from .models import Tournament
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey


class TournamentViewSet(viewsets.ReadOnlyModelViewSet):
    """Tournament viewset."""

    permission_classes = [HasAPIKey | IsAuthenticated]
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer

from django.db import models
from gamehistory.models import Tournament

# Create your models here.


class LiveTournament(models.Model):
    """A live tournament."""

    tournament = models.ForeignKey(Tournament, on_delete=models.PROTECT)

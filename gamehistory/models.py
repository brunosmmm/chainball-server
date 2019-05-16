import datetime

from django.db import models

from player_registry.models import Player
from annoying.fields import JSONField
from collections import deque

# Create your models here.


class InvalidGameActionError(Exception):
    """Invalid game action."""


class Season(models.Model):
    """A complete season."""

    year = models.SmallIntegerField(primary_key=True)
    tournaments = models.ManyToManyField(
        "Tournament", related_name="+", blank=True
    )

    def __str__(self):
        """Get representation."""
        return str(self.year)


class Tournament(models.Model):
    """A Chainball Tournament."""

    TOURNAMENT_UPCOMING = "NYET"
    TOURNAMENT_LIVE = "LIVE"
    TOURNAMENT_DONE = "DONE"

    TOURNAMENT_STATUS = (
        (TOURNAMENT_UPCOMING, "Upcoming"),
        (TOURNAMENT_LIVE, "Live"),
        (TOURNAMENT_DONE, "Finished"),
    )

    season = models.ForeignKey(Season, on_delete=models.PROTECT)
    description = models.CharField(max_length=100)
    event_date = models.DateField("event date")
    players = models.ManyToManyField(Player, blank=True)
    games = models.ManyToManyField("Game", related_name="+", blank=True)
    status = models.CharField(
        max_length=4, choices=TOURNAMENT_STATUS, default=TOURNAMENT_UPCOMING
    )
    ranking = models.ManyToManyField(
        "PlayerRanking", related_name="tournament_ranking", blank=True
    )

    def get_champion(self):
        """Get tournament champion."""
        if self.status != self.TOURNAMENT_DONE:
            raise ValueError("tournament isnt finished yet")

        return self.get_ranking_sorted[0]

    def get_ranking_sorted(self):
        """Get ranking."""
        raise NotImplementedError

    def __str__(self):
        """Get representation."""
        return "{} {}".format(self.season, self.description)


class PlayerRanking(models.Model):
    """Player ranking in tournament."""

    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    tournament = models.ForeignKey(Tournament, on_delete=models.PROTECT)
    victory_points = models.PositiveSmallIntegerField()
    raw_points = models.SmallIntegerField()
    games_played = models.ManyToManyField("Game")


class GameEvent(models.Model):
    """Game event."""

    SCORE_CHANGE = "SCORE_CHANGE"
    SCORE_FORCED = "SCORE_FORCED"
    COWOUT = "COWOUT"
    GAME_START = "GAME_START"
    GAME_END = "GAME_END"
    GAME_PAUSE = "GAME_PAUSE"
    GAME_UNPAUSE = "GAME_UNPAUSE"
    FORCE_SERVE = "FORCE_SERVE"
    DEADBALL = "DEADBALL"
    MUDSKIPPER = "MUDSKIPPER"
    BALL_HIT = "BALL_HIT"
    SAILORMOON = "SAILORMOON"
    CHAINBALL = "CHAINBALL"
    JAILBREAK = "JAILBREAK"
    FAULT = "FAULT"
    DOUBLEFAULT = "DOUBLEFAULT"
    SLOWPOKE = "SLOWPOKE"
    SERVE_ADVANCE = "SERVE_ADVANCE"

    GAME_EVENTS = (
        (SAILORMOON, "Sailor Moon"),
        (MUDSKIPPER, "Mudskipper"),
        (BALL_HIT, "Self hit"),
        (DOUBLEFAULT, "Double fault"),
        (DEADBALL, "Dead ball"),
        (CHAINBALL, "Chainball"),
        (JAILBREAK, "Jailbreak"),
        (SLOWPOKE, "Slow poke"),
        (COWOUT, "Cow out"),
        (SCORE_CHANGE, "score changed"),
        (SCORE_FORCED, "score forced"),
        (COWOUT, "cow out"),
        (GAME_START, "game start"),
        (GAME_END, "game end"),
        (GAME_PAUSE, "game paused"),
        (GAME_UNPAUSE, "game unpaused"),
        (FORCE_SERVE, "force serve"),
        (SERVE_ADVANCE, "serve advanced"),
    )

    EVENT_SCORE_DIFF = {
        SAILORMOON: -2,
        MUDSKIPPER: -1,
        BALL_HIT: -1,
        DOUBLEFAULT: -1,
        DEADBALL: 0,
        CHAINBALL: 1,
        JAILBREAK: 2,
    }

    event = models.CharField(max_length=16, choices=GAME_EVENTS)
    data = JSONField(blank=True)

    def get_point_diff(self):
        """Get point differential"""
        return self.EVENT_SCORE_DIFF[str(self.event)]


class Game(models.Model):
    """Chainball game."""

    GAME_LIVE = "LIVE"
    GAME_DONE = "DONE"
    GAME_UPCOMING = "NYET"

    GAME_STATUS = (
        (GAME_LIVE, "Live"),
        (GAME_DONE, "Finished"),
        (GAME_UPCOMING, "Upcoming"),
    )

    identifier = models.AutoField(primary_key=True)
    sequence = models.SmallIntegerField("game number", default=1)
    description = models.CharField(max_length=16, blank=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    events = models.ManyToManyField(GameEvent, blank=True, editable=False)
    players = models.ManyToManyField(Player)
    duration = models.DurationField(
        "game duration", default=datetime.timedelta(minutes=20), blank=True
    )
    start_time = models.DateTimeField(
        "game start time", blank=True, default=datetime.datetime.now
    )
    game_status = models.CharField(
        max_length=4, choices=GAME_STATUS, default=GAME_UPCOMING
    )

    player_order = models.CharField(blank=True, editable=False, max_length=16)

    def __init__(self, *args, **kwargs):
        """Initialize."""
        super().__init__(*args, **kwargs)
        self._event_history = deque()

    def get_player_names(self):
        """Get players."""
        return [player.name for player in self.players.all()]

    def get_scores(self):
        """Generate score from events."""
        player_scores = {}
        for event in self.events.all():
            player = event.get_player().name
            if player not in player_scores:
                player_scores[player] = event.get_point_diff()
            else:
                player_scores[player] += event.get_point_diff()

        return player_scores

    def start_game(self, start_time, player_order):
        """Flag game as started."""
        if self.game_status == self.GAME_UPCOMING:
            self.game_status = self.GAME_LIVE
            self.save()
        else:
            raise InvalidGameActionError("cannot start game")

    def stop_game(self, reason, winner, running_time, remaining_time):
        """Flag game as stopped (finished)."""
        if self.game_status == self.GAME_LIVE:
            self.game_status = self.GAME_DONE
            self.duration = datetime.timedelta(seconds=running_time)
            self.save()
        else:
            raise InvalidGameActionError("cannot stop game")

    def push_event(self, evt_type, evt_data):
        """Push event."""
        if self.game_status != self.GAME_LIVE:
            raise InvalidGameActionError("game is not live")

        # create new event
        new_event = GameEvent(event=evt_type, data=evt_data)
        new_event.save()
        self.events.add(new_event)
        self._event_history.append(new_event.id)
        self.save()

    def undo_last_event(self):
        """Undo last event."""
        if self.game_status != self.GAME_LIVE:
            raise InvalidGameActionError("game is not live")

        # remove last event
        try:
            evt_id = self._event_history.popleft()
        except IndexError:
            # no events to be popped
            raise InvalidGameActionError("no events to undo")

        # unlink event and destroy
        evt = GameEvent.objects.get(pk=evt_id)
        self.events.remove(evt)
        evt.delete()
        self.save()

    @property
    def event_history(self):
        """Get event history."""
        return self._event_history.copy()

    def __str__(self):
        """Get representation."""
        return "Game {} ({})".format(self.identifier, self.tournament)

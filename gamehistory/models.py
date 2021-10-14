import datetime

from django.db import models
from django.core.exceptions import ValidationError

from player_registry.models import Player
from annoying.fields import JSONField

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


class TournamentLocation(models.Model):
    """Tournament location."""

    name = models.CharField(max_length=40)
    courts = models.ManyToManyField(
        "TournamentCourt", related_name="+", blank=True
    )

    def __str__(self):
        """Get representation."""
        return self.name


class TournamentCourt(models.Model):
    """Game court."""

    number = models.SmallIntegerField()
    location = models.ForeignKey(TournamentLocation, on_delete=models.PROTECT)

    def __str__(self):
        """Get representation."""
        return "{} court {}".format(self.location, self.number)

    def save(self):
        """Save."""
        self.clean()
        super().save()
        self.location.courts.add(self)


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
        "PlayerRanking",
        related_name="tournament_ranking",
        blank=True,
        verbose_name="Player entries",
        help_text="Player entries with associated tournament player number",
    )
    location = models.ForeignKey(TournamentLocation, on_delete=models.PROTECT)

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

    def get_game_id_list(self):
        """Get game list."""
        return [game.sequence for game in self.games.all()]

    def get_player_count(self):
        """Get player count."""
        return len(self.ranking.all())

    def get_player_tids(self):
        """Get registered player by tournament ID."""
        return [player.player_tid for player in self.ranking.all()]

    def get_participating_players(self):
        """Get registered and participating players."""
        return [player.player for player in self.ranking.all()]

    def save(self):
        """Save."""
        self.clean()
        super().save()
        self.players.clear()
        for player in self.get_participating_players():
            self.players.add(player)
        super().save()


class PlayerRanking(models.Model):
    """Player ranking in tournament."""

    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    tournament = models.ForeignKey(Tournament, on_delete=models.PROTECT)
    victory_points = models.PositiveSmallIntegerField(default=0)
    raw_points = models.SmallIntegerField(default=0)
    games_played = models.ManyToManyField("Game", blank=True)
    player_tid = models.SmallIntegerField(
        default=1,
        verbose_name="Player number",
        help_text="Tournament player number",
    )

    class Meta:
        """Adjust stuff."""

        verbose_name = "player entry"
        verbose_name_plural = "player entries"

    def save(self):
        """Save."""
        tournament_player_count = self.tournament.get_player_count()
        registered_tids = self.tournament.get_player_tids()
        registered_players = self.tournament.get_participating_players()
        if self.player in registered_players:
            raise ValidationError(
                f"Player {self.player.name} already registered for tournament"
            )
        if self.player_tid <= tournament_player_count:
            self.player_tid = tournament_player_count + 1
        if self.player_tid in registered_tids:
            raise ValidationError(
                f"Player number {self.player_tid} is already registered"
            )
        # automatically number if necessary
        super().save()
        self.tournament.ranking.add(self)

    def __str__(self):
        """Get string representation."""
        return f"({self.tournament}) {self.player_tid} - {self.player.name}"


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

    def get_player(self):
        """Get player."""
        return self.data.get("player")


def validate_game_score(score):
    """Validate score."""
    if score < -10 or score > 6:
        raise ValidationError("invalid score value")


class GameAnnounce(models.Model):
    """Dummy class to initiate chainbot announcements."""

    identifier = models.AutoField(primary_key=True)
    players = models.ManyToManyField(Player, blank=True, related_name="+")
    court = models.ForeignKey(
        TournamentCourt,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=None,
    )

    # def __str__(self):
    #     """Get representation."""
    #     return "Court call"


class Game(models.Model):
    """Chainball game."""

    GAME_LIVE = "LIVE"
    GAME_DONE = "DONE"
    GAME_UPCOMING = "NYET"
    GAME_NEXT = "NEXT"

    GAME_STATUS = (
        (GAME_LIVE, "Live"),
        (GAME_DONE, "Finished"),
        (GAME_UPCOMING, "Upcoming"),
        (GAME_NEXT, "Next"),
    )

    identifier = models.AutoField(primary_key=True)
    sequence = models.SmallIntegerField("game number", default=1)
    description = models.CharField(max_length=16, blank=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    events = models.ManyToManyField(GameEvent, blank=True, editable=False)
    players = models.ManyToManyField(Player, blank=True)
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
    court = models.ForeignKey(
        TournamentCourt,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=None,
    )

    entries = models.ManyToManyField(
        "PlayerRanking",
        related_name="tournament_entry",
        verbose_name="Player entries",
        help_text="Player entries with associated tournament player number",
    )

    p0_score = models.SmallIntegerField(
        "Player #1 score", default=0, validators=[validate_game_score]
    )
    p1_score = models.SmallIntegerField(
        "Player #2 score", default=0, validators=[validate_game_score]
    )
    p2_score = models.SmallIntegerField(
        "Player #3 score", default=0, validators=[validate_game_score]
    )
    p3_score = models.SmallIntegerField(
        "Player #4 score", default=0, validators=[validate_game_score]
    )

    event_history = JSONField(null=True, blank=True, editable=False)

    def clean(self):
        """Validate."""
        if self.court_id is not None:
            if self.court.location != self.tournament.location:
                raise ValidationError(
                    "Court location must be the same as tournament location."
                )
        # if self.game_status not in ("NYET", "NEXT") and (
        #     self.players.count() < 2 or self.players.count() > 4
        # ):
        #     raise ValidationError("Unsupported player count")
        super().clean()

    def save(self):
        """Save."""
        self.clean()
        # if self.sequence in self.tournament.get_game_id_list():
        #     raise ValidationError("Game # already in tournament")
        super().save()
        self.players.clear()
        for player in self.get_participating_players():
            self.players.add(player)
        super().save()
        self.tournament.games.add(self)

    def get_participating_players(self):
        """Get participating players."""
        return [entry.player for entry in self.entries.all()]

    def get_player_names(self):
        """Get players."""
        return [player.name for player in self.players.all()]

    def get_scores(self):
        """Generate score from events."""
        player_scores = {0: 0, 1: 0, 2: 0, 3: 0}
        if self.event_history is None:
            return player_scores
        history = self.event_history.get("history")
        if history is None:
            return player_scores
        for event_id in history:
            event = GameEvent.objects.get(id=event_id)
            player = event.get_player()
            if player not in player_scores:
                player_scores[player] = event.get_point_diff()
            else:
                player_scores[player] += event.get_point_diff()

        return player_scores

    def _refresh_scores(self):
        scores = self.get_scores()
        for pnum, pscore in scores.items():
            try:
                setattr(self, f"p{pnum}_score", pscore)
            except AttributeError:
                continue

    def start_game(self, start_time, player_order):
        """Flag game as started."""
        if self.game_status in (self.GAME_UPCOMING, self.GAME_NEXT):
            self.game_status = self.GAME_LIVE
            self.player_order = player_order
            self.start_time = datetime.datetime.now()
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
            raise InvalidGameActionError("game is already queued")

    def set_next(self, announce=False):
        """Flag game as next."""
        if self.game_status == self.GAME_UPCOMING:
            self.game_status = self.GAME_NEXT
            self.save()
        else:
            raise InvalidGameActionError("cannot stop game")

        if announce is True:
            _announce = GameAnnounce(court=self.court)
            _announce.save()
            for player in self.players.all():
                _announce.players.add(player)
            _announce.save()

    def reset_state(self):
        """Reset state to upcoming."""
        self.game_status = self.GAME_UPCOMING
        self.save()

    def push_event(self, evt_type, evt_data):
        """Push event."""
        if self.game_status != self.GAME_LIVE:
            raise InvalidGameActionError("game is not live")

        # create new event
        new_event = GameEvent(event=evt_type, data=evt_data)
        new_event.save()
        self.events.add(new_event)

        # event history includes only undoable events!
        if evt_type in GameEvent.EVENT_SCORE_DIFF:
            if self.event_history is None:
                self.event_history = {}
            history = self.event_history.get("history")
            if history is None:
                _history = [new_event.id]
                self.event_history["history"] = _history
            else:
                history.append(new_event.id)
                self.event_history["history"] = history

        self._refresh_scores()
        self.save()

    def undo_last_event(self):
        """Undo last event."""
        if self.game_status != self.GAME_LIVE:
            raise InvalidGameActionError("game is not live")

        # remove last event
        history = self.event_history.get("history")
        if history is None or not history:
            raise InvalidGameActionError("no events to undo")

        del history[-1]
        self.event_history["history"] = history

        # unlink event and destroy
        evt = GameEvent.objects.get(pk=evt_id)
        self.events.remove(evt)
        evt.delete()
        self._refresh_scores()
        self.save()

    @property
    def player_order_list(self):
        """Get player order."""
        order_str = self.player_order
        return [pstr.strip() for pstr in order_str.split(",")]

    @property
    def game_event_history(self):
        """Get event history."""
        return self._event_history.copy()

    def __str__(self):
        """Get representation."""
        return "Game {} ({})".format(self.sequence, self.tournament)

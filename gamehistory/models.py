from django.db import models
from player_registry.models import Player

# Create your models here.


class Season(models.Model):
    """A complete season."""

    year = models.SmallIntegerField()
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


class Game(models.Model):
    """Chainball game."""

    GAME_LIVE = "LIVE"
    GAME_DONE = "DONE"

    GAME_STATUS = ((GAME_LIVE, "Live"), (GAME_DONE, "Finished"))

    identifier = models.CharField(max_length=16)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    events = models.ManyToManyField("GameEvent")
    players = models.ManyToManyField(Player)
    duration = models.DurationField("game duration")
    start_time = models.DateField("game start time")
    game_status = models.CharField(
        max_length=4, choices=GAME_STATUS, default=GAME_DONE
    )

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


class GameEvent(models.Model):
    """Game event."""

    SAILOR_MOON = "SM"
    MUD_SKIPPER = "MS"
    SELF_HIT = "SH"
    DOUBLE_FAULT = "DF"
    DEAD_BALL = "DB"
    CHAIN_BALL = "CB"
    JAIL_BREAK = "JB"
    COW_OUT = "CO"
    SLOW_POKE = "SP"

    GAME_EVENTS = (
        (SAILOR_MOON, "Sailor Moon"),
        (MUD_SKIPPER, "Mudskipper"),
        (SELF_HIT, "Self hit"),
        (DOUBLE_FAULT, "Double fault"),
        (DEAD_BALL, "Dead ball"),
        (CHAIN_BALL, "Chainball"),
        (JAIL_BREAK, "Jailbreak"),
        (SLOW_POKE, "Slow poke"),
        (COW_OUT, "Cow out"),
    )

    EVENT_SCORE_DIFF = {
        SAILOR_MOON: -2,
        MUD_SKIPPER: -1,
        SELF_HIT: -1,
        DOUBLE_FAULT: -1,
        DEAD_BALL: 0,
        CHAIN_BALL: 1,
        JAIL_BREAK: 2,
    }

    # game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    event = models.CharField(max_length=2, choices=GAME_EVENTS)
    game_time = models.SmallIntegerField()

    def get_point_diff(self):
        """Get point differential"""
        return self.EVENT_SCORE_DIFF[str(self.event)]

    def get_player(self):
        """Get player."""
        return self.player

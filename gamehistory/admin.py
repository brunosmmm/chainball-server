"""Admin page configuration."""
from django.contrib import admin, messages
from .models import (
    TournamentLocation,
    TournamentCourt,
    Tournament,
    Season,
    Game,
    GameAnnounce,
    PlayerRanking,
    InvalidGameActionError,
)

from django import forms


class GameForm(forms.ModelForm):
    """Game form."""

    def __init__(self, *args, **kwargs):
        """Initialize."""
        super().__init__(*args, **kwargs)
        self.fields["players"].disabled = True
        if self.fields["game_status"] in ("DONE", "LIVE"):
            # disallow editing of player list
            self.fields["court"].disabled = True
            self.fields["sequence"].disabled = True
            self.fields["tournament"].disabled = True
            self.fields["duration"].disabled = True
            self.fields["entries"].disabled = True

        if self.fields["game_status"] in ("NYET", "NEXT"):
            self.fields["p0_score"].disabled = True
            self.fields["p1_score"].disabled = True
            self.fields["p2_score"].disabled = True
            self.fields["p3_score"].disabled = True
        # else:
        #     player_count = self.fields["players"].count()
        #     if player_count < 4:
        #         self.fields["p3_score"].disabled = True
        #     if player_count < 3:
        #         self.fields["p2_score"].disabled = True

    def clean(self):
        """Clean."""
        cleaned_data = super().clean()
        # tournament_games = cleaned_data["tournament"].get_game_id_list()
        # game_seq = cleaned_data["sequence"]
        # if game_seq in tournament_games:
        #     raise forms.ValidationError(
        #         f"Game #{game_seq} already registed in tournament"
        #     )
        return cleaned_data


class GameAdmin(admin.ModelAdmin):
    """Game Admin form."""

    list_display = ("sequence", "tournament", "start_time")
    list_filter = ("tournament", "start_time")
    actions = ["announce_games", "reset_announce_state"]
    form = GameForm

    @admin.action(description="Set games as unannounced")
    def reset_announce_state(self, request, queryset):
        """Announce games."""
        # set games as upcoming
        for game in queryset:
            if game.game_status == game.GAME_NEXT:
                game.reset_state()
            else:
                self.message_user(
                    request,
                    f"Game #{game.sequence} cannot be re-announced",
                    messages.ERROR,
                )
                continue

    @admin.action(description="Announce games")
    def announce_games(self, request, queryset):
        """Announce games."""
        tournaments = list({game.tournament for game in queryset})
        if len(tournaments) > 1:
            self.message_user(
                request,
                "Selected games must be in the same tournament",
                messages.ERROR,
            )
            return
        location = tournaments[0].location
        court_count = len(location.courts.all())
        if len(queryset) > court_count:
            self.message_user(
                request,
                f"Cannot announce more than {court_count} games at a time",
                messages.ERROR,
            )
            return

        for game in queryset:
            if game.court is None:
                self.message_user(
                    request,
                    f"Game #{game.sequence} location is not defined, cannot announce",
                    messages.ERROR,
                )
                return
        courts = list({game.court for game in queryset})
        if len(queryset) != len(courts):
            # this means that some games are in the same court
            self.message_user(
                request,
                "Conflicting locations in game selections",
                messages.ERROR,
            )
            return

        # set games as next
        for game in queryset:
            try:
                game.set_next(announce=True)
            except InvalidGameActionError:
                self.message_user(
                    request,
                    f"Game #{game.sequence} is already queued",
                    messages.ERROR,
                )
                continue

            # actually announce
            self.message_user(
                request,
                f"Announcement queued for game #{game.sequence}",
                messages.SUCCESS,
            )


class TournamentForm(forms.ModelForm):
    """Tournament form."""

    def __init__(self, *args, **kwargs):
        """Initialize."""
        super().__init__(*args, **kwargs)
        self.fields["ranking"].disabled = True
        self.fields["players"].disabled = True
        self.fields["games"].disabled = True


class TournamentAdmin(admin.ModelAdmin):
    """Tournament Admin form."""

    list_display = ("description", "season", "location", "event_date")
    form = TournamentForm


class PlayerRankingForm(forms.ModelForm):
    """Tournament form."""

    def __init__(self, *args, **kwargs):
        """Initialize."""
        super().__init__(*args, **kwargs)

    def clean(self):
        """Clean."""
        cleaned_data = super().clean()
        registered_players = cleaned_data[
            "tournament"
        ].get_participating_players()
        player_name = cleaned_data["player"].name
        if cleaned_data["player"] in registered_players:
            raise forms.ValidationError(
                f"Player '{player_name}' is already entered into tournament"
            )
        return cleaned_data


class PlayerRankingAdmin(admin.ModelAdmin):
    """Tournament Admin form."""

    list_display = ("player_tid", "player", "tournament")
    list_filter = ("tournament",)
    form = PlayerRankingForm


# Register your models here.
admin.site.register(Tournament, TournamentAdmin)
admin.site.register(Season)
admin.site.register(Game, GameAdmin)
admin.site.register(TournamentLocation)
admin.site.register(TournamentCourt)
admin.site.register(GameAnnounce)
admin.site.register(PlayerRanking, PlayerRankingAdmin)

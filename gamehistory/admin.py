from django.contrib import admin
from .models import (
    TournamentLocation,
    TournamentCourt,
    Tournament,
    Season,
    Game,
)

from django import forms


class GameForm(forms.ModelForm):
    """Game form."""

    def __init__(self, *args, **kwargs):
        """Initialize."""
        super().__init__(*args, **kwargs)
        if self.fields["game_status"] in ("DONE", "LIVE"):
            # disallow editing of player list
            self.fields["players"].disabled = True
            self.fields["court"].disabled = True
            self.fields["sequence"].disabled = True
            self.fields["tournament"].disabled = True
            self.fields["duration"].disabled = True

        if self.fields["game_status"] in ("NYET", "NEXT"):
            self.fields["p0_score"].disabled = True
            self.fields["p1_score"].disabled = True
            self.fields["p2_score"].disabled = True
            self.fields["p3_score"].disabled = True
        else:
            player_count = self.fields["players"].count()
            if player_count < 4:
                self.fields["p3_score"].disabled = True
            if player_count < 3:
                self.fields["p2_score"].disabled = True


class GameAdmin(admin.ModelAdmin):
    """Game Admin form."""

    def get_changelist_form(self, request, **kwargs):
        """Get change list form."""
        return GameForm


# Register your models here.
admin.site.register(Tournament)
admin.site.register(Season)
admin.site.register(Game, GameAdmin)
admin.site.register(TournamentLocation)
admin.site.register(TournamentCourt)

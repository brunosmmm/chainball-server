from django.contrib import admin
from .models import Player


class PlayerAdmin(admin.ModelAdmin):
    ordering = ["name"]


admin.site.register(Player, PlayerAdmin)

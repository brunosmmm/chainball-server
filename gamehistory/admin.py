from django.contrib import admin
from .models import Tournament, Season, Game

# Register your models here.
admin.site.register(Tournament)
admin.site.register(Season)
admin.site.register(Game)

from django.contrib import admin

# Register your models here.

from .models import Match, Player, PlayerInMatch

admin.site.register(Match)
admin.site.register(Player)
admin.site.register(PlayerInMatch)
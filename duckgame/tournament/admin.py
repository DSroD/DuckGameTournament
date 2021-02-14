from django.contrib import admin

# Register your models here.

from .models import Match, Player, PlayerInMatch, PlayerInvitation, MatchInvitation

admin.site.register(Match)
admin.site.register(Player)
admin.site.register(PlayerInMatch)

admin.site.register(MatchInvitation)
admin.site.register(PlayerInvitation)
from django.contrib import admin

# Register your models here.

from .models import Match
from .models import Player

admin.site.register(Match)
admin.site.register(Player)
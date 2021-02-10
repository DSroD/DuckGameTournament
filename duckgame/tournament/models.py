from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    name = models.CharField(max_length=100)
    total_points = models.IntegerField(default=0)
    player_info = models.TextField(max_length=2000, default="No info provided.")
    user = models.OneToOneField(User, blank=True, on_delete=models.DO_NOTHING, null=True)
    def __str__(self):
        return self.name


#Free for all only!
class Match(models.Model):
    play_date = models.DateTimeField('match datetime')
    players = models.ManyToManyField(Player, related_name='matches', through='PlayerInMatch', through_fields=('match', 'player'))
    finished = models.BooleanField('finished', default=False)
    winners = models.ManyToManyField(Player, related_name='won_matches', blank=True)
    loosers = models.ManyToManyField(Player, related_name='lost_matches', blank=True)
    
    def __str__(self):
        if len(self.players.all()) != 2:
            return "Open slots at " + str(self.play_date)
        if not self.finished:
            return " vs. ".join([player.name for player in self.players.all()])
        return r'<span style="color:green; font-weight:bold;">{}</span> vs. <span style="color:red;">{}</span>'.format(" & ".join([player.name for player in self.winners.all()]), " & ".join([player.name for player in self.loosers.all()]))


class PlayerInMatch(models.Model):
    player = models.ForeignKey(Player, on_delete=models.DO_NOTHING)
    match = models.ForeignKey(Match, on_delete=models.DO_NOTHING)
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.player.name + " in " + str(self.match)
    
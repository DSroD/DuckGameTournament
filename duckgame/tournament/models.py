from django.db import models

class Player(models.Model):
    name = models.CharField(max_length=100)
    total_points = models.IntegerField(default=0)
    player_info = models.CharField(max_length=2000, default="No info provided.")
    def __str__(self):
        return self.name


#Free for all only!
class Match(models.Model):
    play_date = models.DateTimeField('match datetime')
    players = models.ManyToManyField(Player, related_name='matches')
    finished = models.BooleanField('finished', default=False)
    winners = models.ManyToManyField(Player, related_name='won_matches', blank=True)
    loosers = models.ManyToManyField(Player, related_name='lost_matches', blank=True)
    
    def __str__(self):
        return " vs. ".join([player.name for player in self.players.all()])


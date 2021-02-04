from django.db import models

class Player(models.Model):
    name = models.CharField(max_length=100)
    wins = models.IntegerField(default=0)
    looses = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)
    player_info = models.CharField(max_length=2000, default="No info provided.")

    def __str__(self):
        return self.name

class Match(models.Model):
    play_date = models.DateTimeField('match datetime')
    players = models.ManyToManyField(Player, related_name='matches')
    finished = models.BooleanField('finished', default=False)
    
    def __str__(self):
        return " vs. ".join([player.name for player in self.players.all()])


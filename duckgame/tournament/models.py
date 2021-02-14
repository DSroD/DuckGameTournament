from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    name = models.CharField(max_length=100)
    total_points = models.IntegerField(default=0)
    player_info = models.TextField(max_length=2000, default="No info provided.")
    user = models.OneToOneField(User, blank=True, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.name


#Free for all only!
class Match(models.Model):
    registrator = models.ForeignKey(Player, on_delete=models.CASCADE, blank=True, null=True)
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
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.player.name + " in " + str(self.match)


class MatchInvitation(models.Model):
    play_date = models.DateTimeField('planned date')
    creator = models.ForeignKey(Player, on_delete=models.CASCADE)
    invited = models.ManyToManyField(Player, related_name='match_invitation', through='PlayerInvitation', through_fields=('match_inv', 'invited_player'))
    creator_is_player = models.BooleanField(default=False)
    auto_create = models.BooleanField('auto_create', default=True)
    class Meta:
        permissions = (("can_create_games", "Can create and plan own games"),)

    def __str__(self):
        return "{}'s game (not confirmed)".format(self.creator.name)
    


class PlayerInvitation(models.Model):
    match_inv = models.ForeignKey(MatchInvitation, on_delete=models.CASCADE, related_name='player_invitations')
    invited_player = models.ForeignKey(Player, on_delete=models.CASCADE)
    accepted = models.BooleanField('accepted', default=False)

    def __str__(self):
        return str(self.match_inv)
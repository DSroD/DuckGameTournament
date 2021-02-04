from django.shortcuts import render

from django.http import Http404

from .models import Match, Player

# Create your views here.
def index(request):
    upcomming_matches = Match.objects.filter(finished=False).order_by("play_date")[:5]
    recently_played = Match.objects.filter(finished=True).order_by("-play_date")[:5]
    context = {'upcomming_matches': upcomming_matches, 'recently_played': recently_played}
    return render(request, 'tournament/index.html', context)

def detail(request, match_id):
    try:
        match = Match.objects.get(pk=match_id)
    except Match.DoesNotExist:
        raise Http404('Match does not exists')
    return render(request, 'tournament/match_detail.html', {'match': match})

def rules(request):
    return render(request, 'tournament/rules.html')

def player(request, player_id):
    try:
        player = Player.objects.get(pk=player_id)
    except Player.DoesNotExist:
        raise Http404('Player does not exists')
    return render(request, 'tournament/player_detail.html', {'player': player})
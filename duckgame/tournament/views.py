from django.shortcuts import render, redirect

from django.contrib.auth import login, authenticate, logout

from django.http import Http404

from .models import Match, Player

from .regform import RegForm

# Create your views here.
def index(request):
    islogged = request.user.is_authenticated
    upcomming_matches = Match.objects.filter(finished=False).order_by("play_date")[:5]
    recently_played = Match.objects.filter(finished=True).order_by("-play_date")[:5]
    context = {'upcomming_matches': upcomming_matches, 'recently_played': recently_played, 'logged_user': islogged}
    return render(request, 'tournament/index.html', context)

def detail(request, match_id):
    try:
        match = Match.objects.get(pk=match_id)
    except Match.DoesNotExist:
        raise Http404('Match does not exists')
    islogged = request.user.is_authenticated
    return render(request, 'tournament/match_detail.html', {'match': match, 'logged_user': islogged})

def rules(request):
    islogged = request.user.is_authenticated
    return render(request, 'tournament/rules.html', {'logged_user': islogged})

def player(request, player_id):
    try:
        player = Player.objects.get(pk=player_id)
    except Player.DoesNotExist:
        raise Http404('Player does not exists')
    islogged = request.user.is_authenticated
    return render(request, 'tournament/player_detail.html', {'player': player, 'logged_user': islogged})

def register(request):
    regwrong = False
    if request.method == 'POST':
        form = RegForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('tournament:index')
        else:
            regwrong = True
    if(request.user.is_authenticated):
        return redirect('tournament:index')
    return render(request, 'tournament/register.html', {'regwrong': regwrong})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('tournament:index')
    if(request.user.is_authenticated):
        return redirect('tournament:index')
    return render(request, 'tournament/login.html')

def logout_view(request):
    if(request.user.is_authenticated):
        logout(request)
    return redirect('tournament:index')
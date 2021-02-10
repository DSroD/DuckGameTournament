from django.shortcuts import render, redirect

from django.contrib.auth import login, authenticate, logout

from django.http import Http404, JsonResponse

from .models import Match, Player, PlayerInMatch

from .regform import RegForm

from .profile_forms import GameAccountCreateForm, GameAccountProfileInfoUpdateForm

# Create your views here.
def index(request):
    islogged = request.user.is_authenticated
    upcomming_matches = Match.objects.filter(finished=False).order_by("play_date")[:10]
    recently_played = Match.objects.filter(finished=True).order_by("-play_date")[:10]
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
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        if username and password:
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


def profile_view(request):
    if(not request.user.is_authenticated):
        return redirect('tournament:login')
    if request.method == 'POST':
        if request.POST.get('game_nick', '') != '' and not hasattr(request.user, 'player'):
            form = GameAccountCreateForm(request.POST)
            if form.is_valid():
                nick = form.cleaned_data.get('game_nick')
                np = Player(name=nick, total_points=0, user=request.user)
                np.save()
        if request.POST.get('profile_text', '') != '' and hasattr(request.user, 'player'):
            form = GameAccountProfileInfoUpdateForm(request.POST)
            if form.is_valid():
                request.user.player.player_info = form.cleaned_data.get('profile_text')
                request.user.player.save(update_fields=['player_info'])
    return render(request, 'tournament/profile.html')


def overlay(request, match_id):
    try:
        match = Match.objects.get(pk=match_id)
    except Match.DoesNotExist:
        raise Http404('Match does not exists')
    return render(request, 'tournament/overlay.html', {'match_id': match_id})


def overlay_update_data(request, match_id):
    try:
        match = Match.objects.get(pk=match_id)
    except Match.DoesNotExist:
        return JsonResponse({'error': 'Match does not exist'})
    match_players = PlayerInMatch.objects.filter(match=match).all()
    plnames = " vs. ".join([pl.player.name for pl in match_players])
    plscore = " : ".join([str(pl.score) for pl in match_players])
    return JsonResponse({'playerstring' : plnames, 'scorestring' : plscore})


def update_view(request, match_id):
    try:
        match = Match.objects.get(pk=match_id)
    except Match.DoesNotExist:
        raise Http404('Match does not exists')
    pim = PlayerInMatch.objects.filter(match=match).all()
    plscore = " : ".join([str(pl.score) for pl in pim])
    return render(request, 'tournament/update.html', {'match' : match, 'score' : plscore})


def update_view_addp(request, match_id, pl_id):
    msg_obj = {'top_message' : 'Point added!'}
    try:
        match = Match.objects.get(pk=match_id)
    except Match.DoesNotExist:
        raise Http404('Match does not exists')

    player = Player.objects.get(pk=pl_id)
    player.total_points += 1
    player.save()
    pp = PlayerInMatch.objects.get(match=match, player=player)
    pp.score += 1
    pp.save()
    pim = PlayerInMatch.objects.filter(match=match).all()
    plscore = " : ".join([str(pl.score) for pl in pim])
    return render(request, 'tournament/update.html', {'match' : match, 'score' : plscore, 'msg_obj' : msg_obj})


def update_view_rmp(request, match_id, pl_id):
    msg_obj = {'top_message' : 'Point removed!'}
    try:
        match = Match.objects.get(pk=match_id)
    except Match.DoesNotExist:
        raise Http404('Match does not exists')

    player = Player.objects.get(pk=pl_id)
    player.total_points -= 1
    player.save()
    pp = PlayerInMatch.objects.get(match=match, player=player)
    pp.score -= 1
    pp.save()
    pim = PlayerInMatch.objects.filter(match=match).all()
    plscore = " : ".join([str(pl.score) for pl in pim])
    return render(request, 'tournament/update.html', {'match' : match, 'score' : plscore, 'msg_obj' : msg_obj})


def update_view_winp(request, match_id, pl_id):
    msg_obj = {'top_message' : 'Winner set!'}
    try:
        match = Match.objects.get(pk=match_id)
    except Match.DoesNotExist:
        raise Http404('Match does not exists')

    pim = PlayerInMatch.objects.filter(match=match).all()
    plscore = " : ".join([str(pl.score) for pl in pim])
    match.finished = True
    match.winners.add(Player.objects.get(pk=pl_id))
    match.save()
    return render(request, 'tournament/update.html', {'match' : match, 'score' : plscore, 'msg_obj' : msg_obj})


def update_view_loosep(request, match_id, pl_id):
    msg_obj = {'top_message' : 'Looser set!'}
    try:
        match = Match.objects.get(pk=match_id)
    except Match.DoesNotExist:
        raise Http404('Match does not exists')

    pim = PlayerInMatch.objects.filter(match=match).all()
    plscore = " : ".join([str(pl.score) for pl in pim])
    match.finished = True
    match.loosers.add(Player.objects.get(pk=pl_id))
    match.save()
    return render(request, 'tournament/update.html', {'match' : match, 'score' : plscore, 'msg_obj' : msg_obj})


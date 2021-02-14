from django.shortcuts import render, redirect

from django.contrib.auth import login, authenticate, logout

from django.contrib.auth.models import User

from django.http import Http404, JsonResponse

from .models import Match, Player, PlayerInMatch, MatchInvitation, PlayerInvitation

from .regform import RegForm

from .profile_forms import GameAccountCreateForm, GameAccountProfileInfoUpdateForm, CreateGameForm

# Create your views here.
def index(request):
    upcomming_matches = Match.objects.filter(finished=False).order_by("play_date")[:10]
    recently_played = Match.objects.filter(finished=True).order_by("-play_date")[:10]
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

    gmform = CreateGameForm(user=request.user)

    try:
        invites = PlayerInvitation.objects.filter(invited_player=request.user.player).order_by("match_inv__play_date")
        my_games = MatchInvitation.objects.filter(creator=request.user.player).order_by("play_date")
        upcomming_matches = Match.objects.filter(finished=False, players=request.user.player).order_by("play_date")[:10]
        recently_played = Match.objects.filter(finished=True, players=request.user.player).order_by("-play_date")[:10]
    except User.player.RelatedObjectDoesNotExist:
        invites = None
        my_games = None
        upcomming_matches = None
        recently_played = None

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
        if request.POST.get('players'):
            gmform = CreateGameForm(request.POST, user=request.user)
            if gmform.is_valid():
                invited_players = gmform.cleaned_data.get('players')
                date = gmform.cleaned_data.get('date')
                reg_as_player = gmform.cleaned_data.get('reg_as_player')
                auto_create = gmform.cleaned_data.get('auto_create')
                # Create new match
                new_inv = MatchInvitation(play_date=date, creator=Player.objects.get(user=request.user), creator_is_player=reg_as_player, auto_create=auto_create)
                new_inv.save()
                for pl in invited_players:
                    p = PlayerInvitation(match_inv=new_inv, invited_player=pl)
                    p.save()
    return render(request, 'tournament/profile.html', {'form' : gmform, 'invites' : invites, 'my_games': my_games, 'upcomming_matches' : upcomming_matches, 'recently_played' : recently_played})


def match_invite_view(request, inv_id):
    can_create = None
    try:
        invite = MatchInvitation.objects.get(pk=inv_id)
    except MatchInvitation.DoesNotExist:
        raise Http404('Invite does not exist')

    if invite.creator == request.user.player or request.user.is_staff:
        player_invite = None
        if len(invite.player_invitations.filter(accepted=False)) == 0:
            can_create = True
        if request.POST.get('action') == 'delete':
            invite.delete()
            return redirect('tournament:profile')

    else:
        try:
            player_invite = PlayerInvitation.objects.get(match_inv=invite, invited_player=request.user.player)
        except PlayerInvitation.DoesNotExist:
            raise Http404('You are not invited')

    if (request.POST.get('action') == 'accept_inv') and player_invite:
        player_invite.accepted = True
        player_invite.save()

    if invite.auto_create or (request.POST.get('action') == 'create' and (invite.creator == request.user.player or request.user.is_staff)):
            if len(invite.player_invitations.filter(accepted=False)) == 0:
                # create game
                new_match = Match(registrator=invite.creator, play_date=invite.play_date)
                new_match.save()
                for inv in invite.player_invitations.all():
                    new_pl = PlayerInMatch(player=inv.invited_player, match=new_match)
                    new_pl.save()
                if invite.creator_is_player:
                    new_pl = PlayerInMatch(player=invite.creator, match=new_match)
                    new_pl.save()

                invite.delete()
                return redirect('tournament:profile')

    elif request.POST.get('action') == 'cancel_inv':
        player_invite.accepted = False
        player_invite.save()
    
    return render(request, 'tournament/invite_detail.html', {'invite' : invite, 'player_invite' : player_invite, 'can_create' : can_create})

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


def invite_view(request, invite_id):
    pass

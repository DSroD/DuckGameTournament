from django import forms
from django.core.validators import RegexValidator

from django.contrib.admin.widgets import AdminSplitDateTime

from django.db.models import Q

from .models import Player

class GameAccountCreateForm(forms.Form):
    game_nick = forms.CharField(min_length=3, max_length=17, validators=[RegexValidator('^[a-zA-Z0-9_\\-]*$'),])

class GameAccountProfileInfoUpdateForm(forms.Form):
    profile_text = forms.CharField(min_length=0, max_length=2000)

class CreateGameForm(forms.Form):
    date = forms.DateTimeField(required=True, input_formats=['%d/%m/%Y %H:%M'], )
    reg_as_player = forms.BooleanField(label="I will participate in the match", required=False)
    auto_create = forms.BooleanField(label="Automatically create game when all players accept invitation", required=False)

    def __init__(self, *args, **kwargs):
         self.user = kwargs.pop('user', None)
         super(CreateGameForm, self).__init__(*args, **kwargs)
         self.fields['players'] = forms.ModelMultipleChoiceField(label="Invited players", queryset=Player.objects.filter(~Q(user=self.user)), widget=forms.SelectMultiple, required=True)
         self.fields['date'].widget.attrs.update({'autocomplete' : 'off'})
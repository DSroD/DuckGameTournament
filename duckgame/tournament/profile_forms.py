from django import forms
from django.core.validators import RegexValidator

class GameAccountCreateForm(forms.Form):
    game_nick = forms.CharField(min_length=3, max_length=17, validators=[RegexValidator('^[a-zA-Z0-9_\\-]*$'),])

class GameAccountProfileInfoUpdateForm(forms.Form):
    profile_text = forms.CharField(min_length=0, max_length=2000, validators=[RegexValidator('^[a-zA-Z0-9_\\- .,&@;\\*\\+]*$')])
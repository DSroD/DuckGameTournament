from django.urls import path

from . import views


app_name='tournament'
urlpatterns = [
    path('', views.index, name='index'),
    path('rules/', views.rules, name='rules'),
    path('matches/<int:match_id>/', views.detail, name='match_detail'),
    path('players/<int:player_id>/', views.player, name='player_detail')
]
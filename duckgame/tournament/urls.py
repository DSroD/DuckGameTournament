from django.urls import path

from . import views


app_name='tournament'
urlpatterns = [
    path('', views.index, name='index'),
    path('rules/', views.rules, name='rules'),
    path('matches/<int:match_id>/', views.detail, name='match_detail'),
    path('players/<int:player_id>/', views.player, name='player_detail'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('overlay/<int:match_id>/', views.overlay, name='overlay'),
    path('overlay/update/<int:match_id>/', views.overlay_update_data, name='overlay_update'),
    path('update/<int:match_id>/', views.update_view, name='update'),
    path('update/<int:match_id>/addp/<int:pl_id>/', views.update_view_addp, name='update_addp'),
    path('update/<int:match_id>/rmp/<int:pl_id>/', views.update_view_rmp, name='update_rmp'),
    path('update/<int:match_id>/win/<int:pl_id>/', views.update_view_winp, name='update_win'),
    path('update/<int:match_id>/loose/<int:pl_id>/', views.update_view_loosep, name='update_loose')
]
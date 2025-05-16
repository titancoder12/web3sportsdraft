from django.urls import path
from . import views

urlpatterns = [
    # Existing URLs
    path('', views.dashboard, name='dashboard'),
    path('division/<int:division_id>/', views.dashboard, name='dashboard_with_division'),
    path('player/<int:player_id>/', views.player_detail, name='player_detail'),
    path('player/profile/', views.player_profile, name='player_profile'),
    path('player/teams/', views.player_teams_view, name='player_teams'),
    path('player/dashboard/', views.player_dashboard, name='player_dashboard'),
    path('add_player/', views.add_player, name='add_player'),
    path('add_player/<int:division_id>/', views.add_player, name='add_player_with_division'),
    path('change_password/', views.change_password, name='change_password'),
    path('signin_log/', views.signin_log_view, name='signin_log'),
    path('verify_stat/<int:stat_id>/', views.verify_stat, name='verify_stat'),
] 
# baseball_draft/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from rest_framework import routers
from league import views
from api import views as api_views
from league.views import request_join_team, review_join_requests, approve_join_request
from league import views as league_views
from league.views import signin_log_view

# REST API
router = routers.DefaultRouter()
router.register(r'players', api_views.PlayerViewSet)
router.register(r'teams', api_views.TeamViewSet)
router.register(r'divisions', api_views.DivisionViewSet)
router.register(r'games', api_views.GameViewSet)
router.register(r'stats', api_views.PlayerGameStatViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='league/login.html'), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', RedirectView.as_view(url='/accounts/login/', permanent=False), name='accounts_home'),
    path('', views.dashboard, name='dashboard'),
    path('division/<int:division_id>/', views.dashboard, name='dashboard_with_division'),
    path('pick/<int:player_id>/<int:division_id>/', views.make_pick, name='make_pick'),
    path('add-player/', views.add_player, name='add_player'),
    path('add-player/<int:division_id>/', views.add_player, name='add_player_with_division'),
    path('profile/', views.player_profile, name='player_profile'),
    path('signup/', views.player_signup, name='player_signup'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('comment/<int:player_id>/<int:division_id>/', views.coach_comment, name='coach_comment'),
    path('draft/', views.public_draft, name='public_draft'),
    path('draft/<int:division_id>/', views.public_draft, name='public_draft_with_division'),
    path('toggle-draft/<int:division_id>/', views.toggle_draft_status, name='toggle_draft_status'),
    path('trade/<int:division_id>/', views.trade_players, name='trade_players'),
    path('player/<int:player_id>/', views.player_detail, name='player_detail'),
    path('import-players/', views.import_players, name='import_players'),  # New route
    path('boxscore/<str:game_id>/', views.box_score_view, name='box_score'),

    # REST API
    path('api/', include(router.urls)), # from router above
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    # API Endpoints for Box Score Uploads
    path('upload-boxscore/', api_views.upload_box_score, name='upload_box_score'),
    path('verify-stats/<int:stat_id>/', api_views.verify_player_stats, name='verify_player_stats'),
    
    # Include league URLs
    path('', include('league.urls')),
]

urlpatterns += [
    path("dashboard/", views.player_dashboard, name="player_dashboard"),
    path('coach/dashboard/', views.coach_dashboard, name='coach_dashboard'),
    path('coach/team/<int:team_id>/add-log/', views.add_team_log, name='add_team_log'),
    path("coach/team/<int:team_id>/logs/", views.team_logs_view, name="team_logs"),
    path("coach/team/log/<int:log_id>/edit/", views.edit_team_log, name="edit_team_log"),
    path("coach/team/log/<int:log_id>/delete/", views.delete_team_log, name="delete_team_log"),
    path("coach/player/<int:player_id>/", views.coach_player_detail, name="coach_player_detail"),
    path("coach/player/<int:player_id>/add-log/", views.add_player_log, name="add_player_log"),
    path("coach/player/log/<int:log_id>/edit/", views.edit_player_log, name="edit_player_log"),
    path("coach/player/log/<int:log_id>/delete/", views.delete_player_log, name="delete_player_log"),
    path('division/team/<int:team_id>/logs/', views.coordinator_team_logs, name='coordinator_team_logs'),
    path("player/logs/", views.player_logs_view, name="player_logs"),
    path('players/<int:player_id>/evaluations/', views.player_evaluations, name='player_evaluations'),
    path('players/<int:player_id>/evaluations/<int:evaluation_id>/', views.get_evaluation_detail, name='evaluation_detail'),
    path("player/teams/", views.player_teams_view, name="player_teams"),
    path('join-team/', request_join_team, name='request_join_team'),
    path('coach/join-requests/', review_join_requests, name='review_join_requests'),
    path('coach/join-requests/<int:request_id>/approve/', approve_join_request, name='approve_join_request'),
    path('find-teams/', views.find_teams, name='find_teams'),
    path('request-join/<int:team_id>/', views.request_join_team, name='request_join_team'),
    path('approve-join-request/<int:request_id>/', views.approve_join_request, name='approve_join_request'),
    path('reject-join-request/<int:request_id>/', views.reject_join_request, name='reject_join_request'),
    path('cancel-request/<int:request_id>/', views.cancel_join_request, name='cancel_join_request'),
    path('re-request/<int:team_id>/', views.re_request_join_team, name='re_request_join_team'),
    path('delete-request/<int:request_id>/', views.delete_join_request, name='delete_join_request'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html'), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    path('account/change-password/', league_views.change_password, name='custom_change_password'),
    path('admin/signin-log/', signin_log_view, name='signin_log'),
]

from league.views import submit_stats, review_stats, verify_stat
urlpatterns += [
    # path('submit-stats/', submit_stats, name='submit_stats'),  # Temporarily disabled
    path('review-stats/', review_stats, name='review_stats'),
    path('coach/verify-stat/<int:stat_id>/', verify_stat, name='verify_stat'),
]
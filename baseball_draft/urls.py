# baseball_draft/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from rest_framework import routers
from league import views
from api import views as api_views

router = routers.DefaultRouter()
router.register(r'players', api_views.PlayerViewSet)

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
    path('signup/', views.signup, name='signup'),
    path('comment/<int:player_id>/<int:division_id>/', views.coach_comment, name='coach_comment'),
    path('draft/', views.public_draft, name='public_draft'),
    path('draft/<int:division_id>/', views.public_draft, name='public_draft_with_division'),
    path('toggle-draft/<int:division_id>/', views.toggle_draft_status, name='toggle_draft_status'),
    path('trade/<int:division_id>/', views.trade_players, name='trade_players'),
    path('player/<int:player_id>/', views.player_detail, name='player_detail'),
    path('import-players/', views.import_players, name='import_players'),  # New route

    # REST API
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
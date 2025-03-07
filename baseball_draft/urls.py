"""baseball_draft URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# baseball_draft/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from league import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='league/login.html'), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', RedirectView.as_view(url='/accounts/login/', permanent=False), name='accounts_home'),
    path('', views.dashboard, name='dashboard'),  # Default dashboard (no division_id)
    path('division/<int:division_id>/', views.dashboard, name='dashboard_with_division'),  # Division-specific
    path('pick/<int:player_id>/<int:division_id>/', views.make_pick, name='make_pick'),
    path('add-player/', views.add_player, name='add_player'),
    path('add-player/<int:division_id>/', views.add_player, name='add_player_with_division'),
    path('profile/', views.player_profile, name='player_profile'),
    path('signup/', views.signup, name='signup'),
    path('comment/<int:player_id>/<int:division_id>/', views.coach_comment, name='coach_comment'),
    path('draft/', views.public_draft, name='public_draft'),
    path('draft/<int:division_id>/', views.public_draft, name='public_draft_with_division'),
]
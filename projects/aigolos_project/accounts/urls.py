"""
URLs for accounts app.
"""

from django.urls import path
from . import views
from . import password_reset

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('api/register/', views.RegisterView.as_view(), name='api_register'),
    path('api/login/', views.login_view, name='api_login'),
    path('api/logout/', views.logout_view, name='api_logout'),
    path('api/profile/', views.profile_view, name='api_profile'),
    path('api/profile/update/', views.update_profile_view, name='api_update_profile'),
    path('api/stats/', views.stats_view, name='api_stats'),
    path('api/password-reset/', password_reset.password_reset_request, name='api_password_reset'),
    path('api/password-reset/confirm/', password_reset.password_reset_confirm, name='api_password_reset_confirm'),
]


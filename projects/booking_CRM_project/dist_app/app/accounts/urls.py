from django.urls import path
from .views import auth_login, auth_register, auth_logout, current_user, dashboard_stats, ensure_csrf
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
	path('login/', auth_login),
	path('register/', auth_register),
	path('logout/', auth_logout),
	path('me/', current_user),
	path('stats/', dashboard_stats),
    path('csrf/', ensure_csrf),
    # JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

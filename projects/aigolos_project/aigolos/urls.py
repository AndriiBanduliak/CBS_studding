"""
URL configuration for AIGolos project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # API v1 (current version)
    path('api/v1/auth/', include(('accounts.urls', 'accounts'), namespace='api_v1_auth')),
    path('api/v1/asr/', include(('asr.urls', 'asr'), namespace='api_v1_asr')),
    path('api/v1/llm/', include(('llm.urls', 'llm'), namespace='api_v1_llm')),
    path('api/v1/tts/', include(('tts.urls', 'tts'), namespace='api_v1_tts')),
    path('api/v1/', include(('core.urls', 'core'), namespace='api_v1')),
    # Legacy API (backward compatibility - redirects to v1)
    path('api/auth/', include('accounts.urls')),
    path('api/asr/', include('asr.urls')),
    path('api/llm/', include('llm.urls')),
    path('api/tts/', include('tts.urls')),
    path('api/', include(('core.urls', 'core'), namespace='api')),
    # Web interface
    path('', RedirectView.as_view(url='/app/', permanent=False)),
    path('app/', include(('core.urls', 'core'), namespace='app')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


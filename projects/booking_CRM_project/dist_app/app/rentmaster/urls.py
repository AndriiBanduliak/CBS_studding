"""
URL configuration for rentmaster project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView, RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.http import FileResponse, Http404
from pathlib import Path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

def serve_static(request, path):
    """Custom static file serving to handle Windows paths correctly"""
    file_path = Path(settings.STATIC_ROOT) / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(open(file_path, 'rb'), content_type='application/javascript' if path.endswith('.js') else 'text/css' if path.endswith('.css') else None)
    raise Http404(f'File not found: {path}')

urlpatterns = [
    # Serve static files FIRST - before everything else
    re_path(r'^static/(?P<path>.*)$', serve_static),
    path("", TemplateView.as_view(template_name="index.html"), name="spa-index"),
    path("admin/", admin.site.urls),
    path("api/", include("properties.urls")),
    path("api/", include("customers.urls")),
    path("api/", include("bookings.urls")),
    path("api/", include("tasks.urls")),
    path("api/auth/", include("accounts.urls")),
    path("api/integrations/", include("integrations.urls")),
    path("api/reports/", include("reports.urls")),
    # API schema & docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

# Catch-all for SPA routes - MUST be LAST, excludes api, admin, static, media
# Static files are served first, so this won't intercept them
urlpatterns += [
    re_path(r'^(?!api|admin|static|media).*$', TemplateView.as_view(template_name="index.html")),
]

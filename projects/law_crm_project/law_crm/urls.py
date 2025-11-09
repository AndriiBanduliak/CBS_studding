"""
URL configuration for law_crm project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('cases/', include('case_management.urls')),
    path('time/', include('time_tracking.urls')),
    path('documents/', include('documents.urls')),
    path('billing/', include('billing.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Настройка админ-панели
admin.site.site_header = "CRM Адвокатського Об'єднання"
admin.site.site_title = "Law CRM"
admin.site.index_title = "Панель управління"


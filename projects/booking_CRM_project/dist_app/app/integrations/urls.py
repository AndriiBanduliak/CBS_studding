from django.urls import path
from . import views

urlpatterns = [
    path('google/start/', views.google_oauth_start),
    path('google/callback/', views.google_oauth_callback),
    path('google/calendars/', views.google_list_calendars),
    path('google/webhook/', views.google_webhook),
    path('google/watch/start/', views.google_watch_start),
    path('google/watch/stop/', views.google_watch_stop),
    path('google/sync/', views.google_sync_now),
    # Channels & Payments placeholders
    path('channels/import-ical/', views.channels_import_ical),
    path('payments/providers/', views.payments_list_providers),
    path('payments/create-intent/', views.payments_create_intent),
    path('payments/webhook/', views.payments_webhook),
]


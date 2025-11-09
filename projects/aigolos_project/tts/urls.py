"""
URLs for TTS app.
"""

from django.urls import path
from . import views

app_name = 'tts'

urlpatterns = [
    path('synthesize/', views.synthesize_view, name='synthesize'),
]


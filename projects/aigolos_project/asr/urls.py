"""
URLs for ASR app.
"""

from django.urls import path
from . import views

app_name = 'asr'

urlpatterns = [
    path('transcribe/', views.transcribe_view, name='transcribe'),
    path('history/', views.TranscriptionListView.as_view(), name='history'),
]


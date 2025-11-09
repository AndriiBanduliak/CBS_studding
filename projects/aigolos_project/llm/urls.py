"""
URLs for LLM app.
"""

from django.urls import path
from . import views

app_name = 'llm'

urlpatterns = [
    path('chat/', views.chat_view, name='chat'),
    path('conversations/', views.ConversationListView.as_view(), name='conversations'),
    path('conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation_detail'),
]


"""
Custom filters for API views.
"""

from rest_framework import filters
from django_filters import rest_framework as django_filters
from django.db import models
from asr.models import Transcription
from llm.models import Conversation


class TranscriptionFilter(django_filters.FilterSet):
    """Filter for Transcription list view."""
    
    language = django_filters.CharFilter(field_name='language', lookup_expr='iexact')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Transcription
        fields = ['language', 'created_after', 'created_before', 'search']
    
    def filter_search(self, queryset, name, value):
        """Search in transcription text."""
        return queryset.filter(text__icontains=value)


class ConversationFilter(django_filters.FilterSet):
    """Filter for Conversation list view."""
    
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_after = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Conversation
        fields = ['title', 'created_after', 'created_before', 'updated_after', 'updated_before', 'search']
    
    def filter_search(self, queryset, name, value):
        """Search in conversation title and messages."""
        return queryset.filter(
            models.Q(title__icontains=value) |
            models.Q(messages__content__icontains=value)
        ).distinct()


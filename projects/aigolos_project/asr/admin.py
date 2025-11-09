"""
Admin configuration for ASR app.
"""

from django.contrib import admin
from .models import Transcription


@admin.register(Transcription)
class TranscriptionAdmin(admin.ModelAdmin):
    """Admin interface for Transcription model."""
    list_display = ('user', 'text_preview', 'language', 'created_at')
    list_filter = ('language', 'created_at')
    search_fields = ('user__username', 'text')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def text_preview(self, obj):
        """Preview of text."""
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text'


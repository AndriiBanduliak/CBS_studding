"""
Admin configuration for TTS app.
"""

from django.contrib import admin
from .models import Synthesis


@admin.register(Synthesis)
class SynthesisAdmin(admin.ModelAdmin):
    """Admin interface for Synthesis model."""
    list_display = ('user', 'text_preview', 'voice', 'created_at')
    list_filter = ('voice', 'created_at')
    search_fields = ('user__username', 'text')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def text_preview(self, obj):
        """Preview of text."""
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text'


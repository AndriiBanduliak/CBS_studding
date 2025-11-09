"""
App configuration for TTS.
"""

from django.apps import AppConfig


class TtsConfig(AppConfig):
    """TTS app configuration."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tts'
    verbose_name = 'TTS'


"""
App configuration for ASR.
"""

from django.apps import AppConfig


class AsrConfig(AppConfig):
    """ASR app configuration."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'asr'
    verbose_name = 'ASR'


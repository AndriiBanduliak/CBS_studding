"""
App configuration for AIGolos.
"""

from django.apps import AppConfig


class AigolosConfig(AppConfig):
    """Main application configuration."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aigolos'
    verbose_name = 'AIGolos'


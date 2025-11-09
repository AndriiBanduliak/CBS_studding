"""
App configuration for LLM.
"""

from django.apps import AppConfig


class LlmConfig(AppConfig):
    """LLM app configuration."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'llm'
    verbose_name = 'LLM'


"""
Models for TTS app.
"""

from django.db import models
from django.conf import settings
import logging

logger = logging.getLogger('tts')


class Synthesis(models.Model):
    """Model for storing TTS syntheses."""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='syntheses')
    text = models.TextField()
    audio_file = models.FileField(upload_to='syntheses/', null=True, blank=True)
    voice = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'syntheses'
        verbose_name = 'Synthesis'
        verbose_name_plural = 'Syntheses'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at}"


"""
Models for ASR app.
"""

from django.db import models
from django.conf import settings
import logging

logger = logging.getLogger('asr')


class Transcription(models.Model):
    """Model for storing transcriptions."""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transcriptions')
    audio_file = models.FileField(upload_to='transcriptions/')
    text = models.TextField()
    language = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'transcriptions'
        verbose_name = 'Transcription'
        verbose_name_plural = 'Transcriptions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at'], name='trans_user_created_idx'),
            models.Index(fields=['language'], name='trans_lang_idx'),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at}"


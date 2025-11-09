"""
Django signals for automatic actions.
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from asr.models import Transcription
from llm.models import Conversation, Message
from tts.models import Synthesis
from accounts.models import User

logger = logging.getLogger('core')


@receiver(post_save, sender=Transcription)
def transcription_created(sender, instance, created, **kwargs):
    """Handle transcription creation."""
    if created:
        # Invalidate cache
        cache.delete(f'transcriptions_{instance.user.id}')
        logger.debug(f"Cache invalidated for user {instance.user.id} transcriptions")


@receiver(post_save, sender=Conversation)
def conversation_updated(sender, instance, created, **kwargs):
    """Handle conversation creation/update."""
    # Invalidate cache
    cache.delete(f'conversations_{instance.user.id}')
    logger.debug(f"Cache invalidated for user {instance.user.id} conversations")


@receiver(post_save, sender=Message)
def message_created(sender, instance, created, **kwargs):
    """Handle message creation."""
    if created:
        # Update conversation's updated_at timestamp
        instance.conversation.updated_at = timezone.now()
        instance.conversation.save(update_fields=['updated_at'])
        
        # Invalidate cache
        cache.delete(f'conversations_{instance.conversation.user.id}')


@receiver(post_delete, sender=Transcription)
def transcription_deleted(sender, instance, **kwargs):
    """Handle transcription deletion."""
    # Invalidate cache
    cache.delete(f'transcriptions_{instance.user.id}')
    
    # Delete associated audio file
    try:
        if instance.audio_file:
            instance.audio_file.delete(save=False)
    except Exception as e:
        logger.warning(f"Failed to delete audio file for transcription {instance.id}: {e}")


@receiver(post_delete, sender=Synthesis)
def synthesis_deleted(sender, instance, **kwargs):
    """Handle synthesis deletion."""
    # Delete associated audio file
    try:
        if instance.audio_file:
            instance.audio_file.delete(save=False)
    except Exception as e:
        logger.warning(f"Failed to delete audio file for synthesis {instance.id}: {e}")


"""
Service layer for views - business logic separated from views.
"""

import logging
from typing import Optional, Tuple
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth import get_user_model
from core.services import asr_service, llm_service, tts_service
from core.validators import validate_audio_file
from core.exceptions import ASRServiceError, LLMServiceError, TTSServiceError
from asr.models import Transcription
from llm.models import Conversation, Message
from tts.models import Synthesis

User = get_user_model()
logger = logging.getLogger('core')


class ASRViewService:
    """Service layer for ASR views."""
    
    @staticmethod
    def transcribe_audio(
        user: User,
        audio_file: UploadedFile,
        language: Optional[str] = None
    ) -> Transcription:
        """
        Transcribe audio file and save to database.
        
        Returns:
            Transcription object
        """
        # Validate file type
        validate_audio_file(audio_file)
        
        # Check file size
        from django.conf import settings
        if audio_file.size > settings.MAX_AUDIO_SIZE:
            raise ValidationError(f'File too large. Maximum size: {settings.MAX_AUDIO_SIZE} bytes')
        
        # Read audio data
        audio_data = audio_file.read()
        
        # Transcribe
        text, detected_language = asr_service.transcribe(audio_data, language)
        
        # Save transcription
        transcription = Transcription.objects.create(
            user=user,
            audio_file=audio_file,
            text=text,
            language=detected_language
        )
        
        # Invalidate cache
        cache.delete(f'transcriptions_{user.id}')
        
        # Record metrics
        from core.metrics import MetricsCollector
        MetricsCollector.record_user_activity(user.id, 'transcription')
        
        logger.info(f"Transcription created: {transcription.id} by {user.username}")
        return transcription


class LLMViewService:
    """Service layer for LLM views."""
    
    @staticmethod
    def process_chat_message(
        user: User,
        message_text: str,
        conversation_id: Optional[int] = None
    ) -> Tuple[Conversation, Message, Message]:
        """
        Process chat message and generate AI response.
        
        Returns:
            Tuple of (conversation, user_message, ai_message)
        """
        # Get or create conversation
        if conversation_id:
            conversation = Conversation.objects.filter(
                id=conversation_id,
                user=user
            ).first()
            if not conversation:
                raise Conversation.DoesNotExist("Conversation not found.")
        else:
            conversation = Conversation.objects.create(
                user=user,
                title=message_text[:50]
            )
        
        # Save user message
        user_message = Message.objects.create(
            conversation=conversation,
            role='user',
            content=message_text
        )
        
        # Generate AI response with conversation context
        ai_response = llm_service.generate(
            message_text,
            str(conversation.id) if conversation_id else None
        )
        
        # Save AI message
        ai_message = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=ai_response
        )
        
        # Update conversation
        if not conversation.title:
            conversation.title = message_text[:50]
        conversation.save()
        
        # Invalidate cache
        cache.delete(f'conversations_{user.id}')
        
        # Record metrics
        from core.metrics import MetricsCollector
        MetricsCollector.record_user_activity(user.id, 'conversation')
        
        logger.info(f"Chat message processed: conversation {conversation.id} by {user.username}")
        return conversation, user_message, ai_message


class TTSViewService:
    """Service layer for TTS views."""
    
    @staticmethod
    def synthesize_text(
        user: User,
        text: str,
        voice: Optional[str] = None
    ) -> Synthesis:
        """
        Synthesize text to speech and save to database.
        
        Returns:
            Synthesis object
        """
        # Synthesize
        audio_data = tts_service.synthesize(text, voice)
        
        # Save synthesis
        from django.core.files.base import ContentFile
        audio_file = ContentFile(audio_data, name='synthesis.wav')
        synthesis = Synthesis.objects.create(
            user=user,
            text=text,
            voice=voice or '',
            audio_file=audio_file
        )
        
        # Record metrics
        from core.metrics import MetricsCollector
        MetricsCollector.record_user_activity(user.id, 'synthesis')
        
        logger.info(f"Synthesis created: {synthesis.id} by {user.username}")
        return synthesis


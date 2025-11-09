"""
Tests for Transcription model.
"""

import pytest
from asr.models import Transcription
from tests.conftest import UserFactory


class TestTranscription:
    """Test cases for Transcription model."""
    
    def test_transcription_creation(self, db):
        """Test transcription creation."""
        user = UserFactory()
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        audio_file = SimpleUploadedFile(
            "test.wav",
            b"fake audio content",
            content_type="audio/wav"
        )
        
        transcription = Transcription.objects.create(
            user=user,
            audio_file=audio_file,
            text='Hello world',
            language='en'
        )
        
        assert transcription.pk is not None
        assert transcription.user == user
        assert transcription.text == 'Hello world'
        assert transcription.language == 'en'
    
    def test_transcription_str(self, db):
        """Test transcription string representation."""
        user = UserFactory()
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        audio_file = SimpleUploadedFile("test.wav", b"content", content_type="audio/wav")
        transcription = Transcription.objects.create(
            user=user,
            audio_file=audio_file,
            text='Test',
            language='en'
        )
        
        assert user.username in str(transcription)
    
    def test_transcription_ordering(self, db):
        """Test that transcriptions are ordered by created_at descending."""
        user = UserFactory()
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        audio1 = SimpleUploadedFile("test1.wav", b"content", content_type="audio/wav")
        audio2 = SimpleUploadedFile("test2.wav", b"content", content_type="audio/wav")
        
        transcription1 = Transcription.objects.create(
            user=user,
            audio_file=audio1,
            text='First',
            language='en'
        )
        transcription2 = Transcription.objects.create(
            user=user,
            audio_file=audio2,
            text='Second',
            language='en'
        )
        
        transcriptions = list(Transcription.objects.all())
        # Most recent should be first
        assert transcriptions[0].created_at >= transcriptions[1].created_at
    
    def test_transcription_language_optional(self, db):
        """Test that language is optional."""
        user = UserFactory()
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        audio_file = SimpleUploadedFile("test.wav", b"content", content_type="audio/wav")
        transcription = Transcription.objects.create(
            user=user,
            audio_file=audio_file,
            text='Test',
            language=None
        )
        
        assert transcription.language is None


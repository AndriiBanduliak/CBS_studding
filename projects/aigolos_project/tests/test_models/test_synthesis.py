"""
Tests for Synthesis model.
"""

import pytest
from tts.models import Synthesis
from tests.conftest import UserFactory


class TestSynthesis:
    """Test cases for Synthesis model."""
    
    def test_synthesis_creation(self, db):
        """Test synthesis creation."""
        user = UserFactory()
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        audio_file = SimpleUploadedFile(
            "test.wav",
            b"fake audio content",
            content_type="audio/wav"
        )
        
        synthesis = Synthesis.objects.create(
            user=user,
            text='Hello world',
            audio_file=audio_file,
            voice='en_US/amy/medium'
        )
        
        assert synthesis.pk is not None
        assert synthesis.user == user
        assert synthesis.text == 'Hello world'
        assert synthesis.voice == 'en_US/amy/medium'
    
    def test_synthesis_str(self, db):
        """Test synthesis string representation."""
        user = UserFactory()
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        audio_file = SimpleUploadedFile("test.wav", b"content", content_type="audio/wav")
        synthesis = Synthesis.objects.create(
            user=user,
            text='Test',
            audio_file=audio_file,
            voice='test_voice'
        )
        
        assert user.username in str(synthesis)
    
    def test_synthesis_ordering(self, db):
        """Test that syntheses are ordered by created_at descending."""
        user = UserFactory()
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        audio1 = SimpleUploadedFile("test1.wav", b"content", content_type="audio/wav")
        audio2 = SimpleUploadedFile("test2.wav", b"content", content_type="audio/wav")
        
        synth1 = Synthesis.objects.create(
            user=user,
            text='First',
            audio_file=audio1,
            voice='voice1'
        )
        synth2 = Synthesis.objects.create(
            user=user,
            text='Second',
            audio_file=audio2,
            voice='voice2'
        )
        
        syntheses = list(Synthesis.objects.all())
        assert syntheses[0].created_at >= syntheses[1].created_at
    
    def test_synthesis_audio_optional(self, db):
        """Test that audio_file is optional."""
        user = UserFactory()
        synthesis = Synthesis.objects.create(
            user=user,
            text='Test',
            audio_file=None,
            voice='test_voice'
        )
        
        assert synthesis.audio_file is None or synthesis.audio_file == ''
    
    def test_synthesis_voice_optional(self, db):
        """Test that voice can be empty."""
        user = UserFactory()
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        audio_file = SimpleUploadedFile("test.wav", b"content", content_type="audio/wav")
        synthesis = Synthesis.objects.create(
            user=user,
            text='Test',
            audio_file=audio_file,
            voice=''
        )
        
        assert synthesis.voice == ''


"""
Tests for ASR views.
"""

import pytest
from unittest.mock import patch, Mock
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from asr.models import Transcription


class TestTranscribeView:
    """Test cases for transcribe_view."""
    
    def test_transcribe_success(self, authenticated_client, user):
        """Test successful transcription."""
        audio_file = SimpleUploadedFile(
            "test.wav",
            b"fake audio content",
            content_type="audio/wav"
        )
        
        with patch('asr.views.asr_service.transcribe') as mock_transcribe:
            mock_transcribe.return_value = ('Hello world', 'en')
            
            response = authenticated_client.post(
                '/api/asr/transcribe/',
                {'audio': audio_file, 'language': 'en'},
                format='multipart'
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            assert 'text' in response.data
            assert response.data['text'] == 'Hello world'
            assert Transcription.objects.filter(user=user).exists()
    
    def test_transcribe_no_file(self, authenticated_client):
        """Test transcription without audio file."""
        response = authenticated_client.post('/api/asr/transcribe/', {})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    def test_transcribe_file_too_large(self, authenticated_client):
        """Test transcription with file too large."""
        from django.conf import settings
        large_file = SimpleUploadedFile(
            "large.wav",
            b"x" * (settings.MAX_AUDIO_SIZE + 1),
            content_type="audio/wav"
        )
        
        response = authenticated_client.post(
            '/api/asr/transcribe/',
            {'audio': large_file},
            format='multipart'
        )
        
        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    
    def test_transcribe_unauthenticated(self, api_client):
        """Test transcription without authentication."""
        audio_file = SimpleUploadedFile("test.wav", b"content", content_type="audio/wav")
        
        response = api_client.post(
            '/api/asr/transcribe/',
            {'audio': audio_file},
            format='multipart'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_transcribe_service_error(self, authenticated_client):
        """Test handling of service errors."""
        audio_file = SimpleUploadedFile("test.wav", b"content", content_type="audio/wav")
        
        with patch('asr.views.asr_service.transcribe') as mock_transcribe:
            mock_transcribe.side_effect = RuntimeError('ASR model is not available')
            
            response = authenticated_client.post(
                '/api/asr/transcribe/',
                {'audio': audio_file},
                format='multipart'
            )
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert 'error' in response.data


class TestTranscriptionListView:
    """Test cases for TranscriptionListView."""
    
    def test_list_transcriptions(self, authenticated_client, user):
        """Test listing user transcriptions."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        audio1 = SimpleUploadedFile("test1.wav", b"content", content_type="audio/wav")
        audio2 = SimpleUploadedFile("test2.wav", b"content", content_type="audio/wav")
        
        Transcription.objects.create(
            user=user,
            audio_file=audio1,
            text='First transcription',
            language='en'
        )
        Transcription.objects.create(
            user=user,
            audio_file=audio2,
            text='Second transcription',
            language='en'
        )
        
        response = authenticated_client.get('/api/asr/history/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_list_empty(self, authenticated_client):
        """Test listing when no transcriptions exist."""
        response = authenticated_client.get('/api/asr/history/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0
    
    def test_list_unauthenticated(self, api_client):
        """Test listing without authentication."""
        response = api_client.get('/api/asr/history/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


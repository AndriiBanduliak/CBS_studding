"""
Integration tests for complete API flows.
"""

import pytest
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.authtoken.models import Token


class TestCompleteUserFlow:
    """Test complete user registration and authentication flow."""
    
    def test_register_and_login(self, api_client):
        """Test user registration and login."""
        # Register
        register_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        
        response = api_client.post('/api/auth/api/register/', register_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'token' in response.data
        
        # Login
        login_data = {
            'username': 'newuser',
            'password': 'testpass123'
        }
        
        response = api_client.post('/api/auth/api/login/', login_data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'token' in response.data
    
    def test_get_profile(self, authenticated_client, user):
        """Test getting user profile."""
        response = authenticated_client.get('/api/auth/api/profile/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username
        assert response.data['email'] == user.email


class TestASRFlow:
    """Test complete ASR flow."""
    
    def test_complete_transcription_flow(self, authenticated_client, user):
        """Test complete transcription workflow."""
        audio_file = SimpleUploadedFile(
            "test.wav",
            b"fake audio content",
            content_type="audio/wav"
        )
        
        with patch('asr.views.asr_service.transcribe') as mock_transcribe:
            mock_transcribe.return_value = ('Transcribed text', 'en')
            
            # Transcribe
            response = authenticated_client.post(
                '/api/asr/transcribe/',
                {'audio': audio_file},
                format='multipart'
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            transcription_id = response.data['id']
            
            # Get history
            response = authenticated_client.get('/api/asr/history/')
            assert response.status_code == status.HTTP_200_OK
            assert any(t['id'] == transcription_id for t in response.data['results'])


class TestLLMFlow:
    """Test complete LLM flow."""
    
    def test_complete_chat_flow(self, authenticated_client, user):
        """Test complete chat workflow."""
        with patch('llm.views.llm_service.generate') as mock_generate:
            mock_generate.return_value = 'AI response'
            
            # Create conversation
            response = authenticated_client.post(
                '/api/llm/chat/',
                {'message': 'Hello'},
                format='json'
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            conversation_id = response.data['conversation_id']
            
            # Continue conversation
            response = authenticated_client.post(
                '/api/llm/chat/',
                {
                    'message': 'How are you?',
                    'conversation_id': conversation_id
                },
                format='json'
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data['conversation_id'] == conversation_id
            
            # List conversations
            response = authenticated_client.get('/api/llm/conversations/')
            assert response.status_code == status.HTTP_200_OK
            assert any(c['id'] == conversation_id for c in response.data['results'])


class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check_authenticated(self, authenticated_client, user):
        """Test health check with authentication."""
        response = authenticated_client.get('/api/health/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'healthy'
        assert response.data['user'] == user.username
    
    def test_health_check_unauthenticated(self, api_client):
        """Test health check without authentication."""
        response = api_client.get('/api/health/')
        
        # Currently requires authentication
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


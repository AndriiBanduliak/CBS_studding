"""
Tests for LLM views.
"""

import pytest
from unittest.mock import patch
from rest_framework import status
from llm.models import Conversation, Message


class TestChatView:
    """Test cases for chat_view."""
    
    def test_chat_success(self, authenticated_client, user):
        """Test successful chat."""
        with patch('llm.views.llm_service.generate') as mock_generate:
            mock_generate.return_value = 'Hello! How can I help you?'
            
            response = authenticated_client.post(
                '/api/llm/chat/',
                {'message': 'Hello'},
                format='json'
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            assert 'conversation_id' in response.data
            assert 'user_message' in response.data
            assert 'ai_message' in response.data
            assert Conversation.objects.filter(user=user).exists()
            assert Message.objects.filter(conversation__user=user).exists()
    
    def test_chat_empty_message(self, authenticated_client):
        """Test chat with empty message."""
        response = authenticated_client.post(
            '/api/llm/chat/',
            {'message': ''},
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    def test_chat_with_existing_conversation(self, authenticated_client, user):
        """Test chat with existing conversation."""
        conversation = Conversation.objects.create(user=user, title='Test')
        
        with patch('llm.views.llm_service.generate') as mock_generate:
            mock_generate.return_value = 'Response'
            
            response = authenticated_client.post(
                '/api/llm/chat/',
                {
                    'message': 'Hello',
                    'conversation_id': str(conversation.id)
                },
                format='json'
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data['conversation_id'] == conversation.id
    
    def test_chat_invalid_conversation(self, authenticated_client, user):
        """Test chat with invalid conversation ID."""
        with patch('llm.views.llm_service.generate') as mock_generate:
            mock_generate.return_value = 'Response'
            
            response = authenticated_client.post(
                '/api/llm/chat/',
                {
                    'message': 'Hello',
                    'conversation_id': 'invalid-id'
                },
                format='json'
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_chat_service_error(self, authenticated_client):
        """Test handling of service errors."""
        with patch('llm.views.llm_service.generate') as mock_generate:
            mock_generate.side_effect = RuntimeError('LLM request failed')
            
            response = authenticated_client.post(
                '/api/llm/chat/',
                {'message': 'Hello'},
                format='json'
            )
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert 'error' in response.data
    
    def test_chat_unauthenticated(self, api_client):
        """Test chat without authentication."""
        response = api_client.post(
            '/api/llm/chat/',
            {'message': 'Hello'},
            format='json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestConversationListView:
    """Test cases for ConversationListView."""
    
    def test_list_conversations(self, authenticated_client, user):
        """Test listing user conversations."""
        Conversation.objects.create(user=user, title='Chat 1')
        Conversation.objects.create(user=user, title='Chat 2')
        
        response = authenticated_client.get('/api/llm/conversations/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_list_empty(self, authenticated_client):
        """Test listing when no conversations exist."""
        response = authenticated_client.get('/api/llm/conversations/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0
    
    def test_list_unauthenticated(self, api_client):
        """Test listing without authentication."""
        response = api_client.get('/api/llm/conversations/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


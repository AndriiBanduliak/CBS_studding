"""
Unit tests for LLM service.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from django.test import override_settings
from core.services import LLMService
import httpx


class TestLLMService:
    """Test cases for LLMService."""
    
    def test_init(self):
        """Test service initialization."""
        with override_settings(
            OLLAMA_BASE_URL='http://localhost:11434',
            LLM_MODEL_NAME='test-model',
            LLM_MAX_TOKENS=256,
            LLM_TEMPERATURE=0.7
        ):
            service = LLMService()
            assert service.base_url == 'http://localhost:11434'
            assert service.model_name == 'test-model'
            assert service.max_tokens == 256
            assert service.temperature == 0.7
            assert service._client is None
    
    def test_client_property(self):
        """Test client property creation."""
        with override_settings(OLLAMA_BASE_URL='http://localhost:11434'):
            service = LLMService()
            client = service.client
            
            assert client is not None
            assert isinstance(client, httpx.Client)
            assert service._client is not None
    
    def test_client_reuse(self):
        """Test that client is reused on subsequent calls."""
        with override_settings(OLLAMA_BASE_URL='http://localhost:11434'):
            service = LLMService()
            client1 = service.client
            client2 = service.client
            
            assert client1 is client2
    
    @patch('core.services.httpx.Client')
    def test_generate_success(self, mock_client_class):
        """Test successful LLM response generation."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {'response': 'Hello, how can I help you?'}
        mock_response.raise_for_status = Mock()
        
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        with override_settings(
            OLLAMA_BASE_URL='http://localhost:11434',
            LLM_MODEL_NAME='test-model',
            LLM_MAX_TOKENS=256,
            LLM_TEMPERATURE=0.7
        ):
            service = LLMService()
            service._client = mock_client
            
            response = service.generate('Hello')
            
            assert response == 'Hello, how can I help you?'
            assert mock_client.post.called
            call_args = mock_client.post.call_args
            assert call_args[0][0] == '/api/generate'
            assert call_args[1]['json']['model'] == 'test-model'
            assert call_args[1]['json']['prompt'] == 'Hello'
    
    @patch('core.services.httpx.Client')
    def test_generate_with_conversation_id(self, mock_client_class):
        """Test generation with conversation ID."""
        mock_response = Mock()
        mock_response.json.return_value = {'response': 'Response'}
        mock_response.raise_for_status = Mock()
        
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        with override_settings(
            OLLAMA_BASE_URL='http://localhost:11434',
            LLM_MODEL_NAME='test-model',
            LLM_MAX_TOKENS=256,
            LLM_TEMPERATURE=0.7
        ):
            service = LLMService()
            service._client = mock_client
            
            response = service.generate('Hello', conversation_id='conv-123')
            
            assert response == 'Response'
            # Note: Currently conversation_id is not used, but parameter is accepted
    
    @patch('core.services.httpx.Client')
    def test_generate_http_error(self, mock_client_class):
        """Test handling of HTTP errors."""
        mock_client = Mock()
        mock_client.post.side_effect = httpx.HTTPError('Connection failed')
        mock_client_class.return_value = mock_client
        
        with override_settings(
            OLLAMA_BASE_URL='http://localhost:11434',
            LLM_MODEL_NAME='test-model',
            LLM_MAX_TOKENS=256,
            LLM_TEMPERATURE=0.7
        ):
            service = LLMService()
            service._client = mock_client
            
            with pytest.raises(RuntimeError, match='LLM request failed'):
                service.generate('Hello')
    
    @patch('core.services.httpx.Client')
    def test_generate_empty_response(self, mock_client_class):
        """Test handling of empty response."""
        mock_response = Mock()
        mock_response.json.return_value = {'response': ''}
        mock_response.raise_for_status = Mock()
        
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        with override_settings(
            OLLAMA_BASE_URL='http://localhost:11434',
            LLM_MODEL_NAME='test-model',
            LLM_MAX_TOKENS=256,
            LLM_TEMPERATURE=0.7
        ):
            service = LLMService()
            service._client = mock_client
            
            response = service.generate('Hello')
            
            assert response == ''
    
    def test_close(self):
        """Test closing the HTTP client."""
        mock_client = Mock()
        
        with override_settings(OLLAMA_BASE_URL='http://localhost:11434'):
            service = LLMService()
            service._client = mock_client
            
            service.close()
            
            assert mock_client.close.called
            assert service._client is None
    
    def test_close_without_client(self):
        """Test close when client doesn't exist."""
        with override_settings(OLLAMA_BASE_URL='http://localhost:11434'):
            service = LLMService()
            service._client = None
            
            # Should not raise an error
            service.close()
            assert service._client is None


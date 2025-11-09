"""
Tests for LoggingMiddleware.
"""

import pytest
from unittest.mock import Mock, patch
from django.test import RequestFactory
from aigolos.middleware import LoggingMiddleware
import time


class TestLoggingMiddleware:
    """Test cases for LoggingMiddleware."""
    
    def test_process_request(self):
        """Test that request start time is recorded."""
        middleware = LoggingMiddleware(get_response=Mock())
        factory = RequestFactory()
        request = factory.get('/test/')
        
        middleware.process_request(request)
        
        assert hasattr(request, '_start_time')
        assert isinstance(request._start_time, float)
    
    def test_process_response(self):
        """Test response logging."""
        middleware = LoggingMiddleware(get_response=Mock())
        factory = RequestFactory()
        request = factory.get('/test/')
        request._start_time = time.time()
        request.user = Mock()
        request.user.username = 'testuser'
        
        response = Mock()
        response.status_code = 200
        
        with patch('aigolos.middleware.logger') as mock_logger:
            result = middleware.process_response(request, response)
            
            assert result == response
            assert mock_logger.info.called
            call_args = mock_logger.info.call_args[0][0]
            assert 'GET' in call_args
            assert '/test/' in call_args
            assert '200' in call_args
            assert 'testuser' in call_args
    
    def test_process_response_anonymous_user(self):
        """Test response logging with anonymous user."""
        middleware = LoggingMiddleware(get_response=Mock())
        factory = RequestFactory()
        request = factory.get('/test/')
        request._start_time = time.time()
        
        response = Mock()
        response.status_code = 200
        
        with patch('aigolos.middleware.logger') as mock_logger:
            middleware.process_response(request, response)
            
            call_args = mock_logger.info.call_args[0][0]
            assert 'Anonymous' in call_args
    
    def test_process_response_no_start_time(self):
        """Test response when start time is not set."""
        middleware = LoggingMiddleware(get_response=Mock())
        factory = RequestFactory()
        request = factory.get('/test/')
        
        response = Mock()
        response.status_code = 200
        
        # Should not raise an error
        result = middleware.process_response(request, response)
        assert result == response
    
    def test_process_exception(self):
        """Test exception logging."""
        middleware = LoggingMiddleware(get_response=Mock())
        factory = RequestFactory()
        request = factory.get('/test/')
        
        exception = ValueError('Test error')
        
        with patch('aigolos.middleware.logger') as mock_logger:
            result = middleware.process_exception(request, exception)
            
            assert result is None
            assert mock_logger.error.called
            call_args = mock_logger.error.call_args
            assert 'GET' in call_args[0][0]
            assert '/test/' in call_args[0][0]
            assert 'Test error' in call_args[0][0]
            # Check that exc_info=True was passed
            assert call_args[1]['exc_info'] is True
    
    def test_process_response_duration_calculation(self):
        """Test that duration is calculated correctly."""
        middleware = LoggingMiddleware(get_response=Mock())
        factory = RequestFactory()
        request = factory.get('/test/')
        request._start_time = time.time() - 0.5  # 0.5 seconds ago
        request.user = Mock()
        request.user.username = 'testuser'
        
        response = Mock()
        response.status_code = 200
        
        with patch('aigolos.middleware.logger') as mock_logger:
            middleware.process_response(request, response)
            
            call_args = mock_logger.info.call_args[0][0]
            assert 'Duration' in call_args
            # Duration should be around 0.5 seconds
            assert '0.' in call_args


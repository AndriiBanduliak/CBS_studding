"""
Unit tests for TTS service.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from django.test import override_settings
from core.services import TTSService
import subprocess
import tempfile
from pathlib import Path


class TestTTSService:
    """Test cases for TTSService."""
    
    def test_init_with_piper(self):
        """Test initialization when Piper is available."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            
            with override_settings(
                TTS_VOICE_NAME='en_US/amy/medium',
                TTS_MODEL_PATH=''
            ):
                service = TTSService()
                # Check that piper was checked
                assert mock_run.called
    
    def test_init_without_piper(self):
        """Test initialization when Piper is not available."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError()
            
            with override_settings(
                TTS_VOICE_NAME='en_US/amy/medium',
                TTS_MODEL_PATH=''
            ):
                service = TTSService()
                # Service should still initialize
    
    @patch('subprocess.run')
    @patch('builtins.open', create=True)
    def test_synthesize_success(self, mock_open, mock_run):
        """Test successful TTS synthesis."""
        # Mock file operations
        mock_file = Mock()
        mock_file.read.return_value = b'fake audio data'
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Mock subprocess
        mock_run.return_value = Mock(returncode=0)
        
        with override_settings(
            TTS_VOICE_NAME='en_US/amy/medium',
            TTS_MODEL_PATH=''
        ):
            service = TTSService()
            
            audio_data = service.synthesize('Hello world')
            
            assert audio_data == b'fake audio data'
            assert mock_run.called
    
    @patch('subprocess.run')
    def test_synthesize_with_custom_voice(self, mock_run):
        """Test synthesis with custom voice."""
        mock_run.return_value = Mock(returncode=0)
        
        with patch('builtins.open', create=True) as mock_open:
            mock_file = Mock()
            mock_file.read.return_value = b'audio data'
            mock_open.return_value.__enter__.return_value = mock_file
            
            with override_settings(
                TTS_VOICE_NAME='en_US/amy/medium',
                TTS_MODEL_PATH=''
            ):
                service = TTSService()
                
                audio_data = service.synthesize('Hello', voice='custom_voice')
                
                assert audio_data == b'audio data'
                # Check that custom voice was used
                call_args = mock_run.call_args
                assert 'custom_voice' in call_args[0][0] or 'custom_voice' in str(call_args)
    
    @patch('subprocess.run')
    def test_synthesize_with_model_path(self, mock_run):
        """Test synthesis with model path."""
        mock_run.return_value = Mock(returncode=0)
        
        with patch('builtins.open', create=True) as mock_open:
            mock_file = Mock()
            mock_file.read.return_value = b'audio data'
            mock_open.return_value.__enter__.return_value = mock_file
            
            with override_settings(
                TTS_VOICE_NAME='en_US/amy/medium',
                TTS_MODEL_PATH='/path/to/model'
            ):
                service = TTSService()
                
                audio_data = service.synthesize('Hello')
                
                assert audio_data == b'audio data'
    
    @patch('subprocess.run')
    def test_synthesize_subprocess_error(self, mock_run):
        """Test handling of subprocess errors."""
        mock_run.return_value = Mock(
            returncode=1,
            stderr=b'Error: Model not found'
        )
        
        with override_settings(
            TTS_VOICE_NAME='en_US/amy/medium',
            TTS_MODEL_PATH=''
        ):
            service = TTSService()
            
            with pytest.raises(RuntimeError, match='Piper TTS failed'):
                service.synthesize('Hello')
    
    @patch('subprocess.run')
    def test_synthesize_timeout(self, mock_run):
        """Test handling of timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired('piper', 30)
        
        with override_settings(
            TTS_VOICE_NAME='en_US/amy/medium',
            TTS_MODEL_PATH=''
        ):
            service = TTSService()
            
            with pytest.raises(RuntimeError, match='TTS synthesis timed out'):
                service.synthesize('Hello')
    
    @patch('subprocess.run')
    def test_synthesize_general_exception(self, mock_run):
        """Test handling of general exceptions."""
        mock_run.side_effect = Exception('Unexpected error')
        
        with override_settings(
            TTS_VOICE_NAME='en_US/amy/medium',
            TTS_MODEL_PATH=''
        ):
            service = TTSService()
            
            with pytest.raises(RuntimeError, match='TTS synthesis failed'):
                service.synthesize('Hello')
    
    def test_synthesize_empty_text(self):
        """Test synthesis with empty text."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            
            with patch('builtins.open', create=True) as mock_open:
                mock_file = Mock()
                mock_file.read.return_value = b''
                mock_open.return_value.__enter__.return_value = mock_file
                
                with override_settings(
                    TTS_VOICE_NAME='en_US/amy/medium',
                    TTS_MODEL_PATH=''
                ):
                    service = TTSService()
                    
                    audio_data = service.synthesize('')
                    
                    assert audio_data == b''


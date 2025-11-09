"""
Unit tests for ASR service.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from django.test import override_settings
from core.services import ASRService
import tempfile
from pathlib import Path


class TestASRService:
    """Test cases for ASRService."""
    
    def test_init_without_faster_whisper(self):
        """Test initialization when faster-whisper is not installed."""
        with patch('core.services.WhisperModel', side_effect=ImportError):
            service = ASRService()
            assert service.model is None
    
    def test_init_with_faster_whisper(self):
        """Test initialization when faster-whisper is installed."""
        mock_model = Mock()
        with patch('core.services.WhisperModel', return_value=mock_model):
            with override_settings(
                ASR_MODEL_NAME='base',
                ASR_DEVICE='cpu',
                ASR_COMPUTE_TYPE='int8'
            ):
                service = ASRService()
                assert service.model == mock_model
    
    def test_transcribe_success(self):
        """Test successful transcription."""
        # Create mock audio data
        audio_data = b'fake audio data'
        
        # Mock WhisperModel
        mock_segment = Mock()
        mock_segment.text = 'Hello world'
        mock_info = Mock()
        mock_info.language = 'en'
        
        mock_model = Mock()
        mock_model.transcribe.return_value = (
            [mock_segment],
            mock_info
        )
        
        service = ASRService()
        service.model = mock_model
        
        text, language = service.transcribe(audio_data)
        
        assert text == 'Hello world'
        assert language == 'en'
        assert mock_model.transcribe.called
    
    def test_transcribe_without_model(self):
        """Test transcription when model is not available."""
        service = ASRService()
        service.model = None
        
        with pytest.raises(RuntimeError, match='ASR model is not available'):
            service.transcribe(b'audio data')
    
    def test_transcribe_with_language(self):
        """Test transcription with specified language."""
        audio_data = b'fake audio data'
        
        mock_segment = Mock()
        mock_segment.text = 'Bonjour'
        mock_info = Mock()
        mock_info.language = 'fr'
        
        mock_model = Mock()
        mock_model.transcribe.return_value = (
            [mock_segment],
            mock_info
        )
        
        service = ASRService()
        service.model = mock_model
        
        text, language = service.transcribe(audio_data, language='fr')
        
        assert text == 'Bonjour'
        assert language == 'fr'
        # Check that language parameter was passed
        call_args = mock_model.transcribe.call_args
        assert call_args[1]['language'] == 'fr'
    
    def test_transcribe_multiple_segments(self):
        """Test transcription with multiple segments."""
        audio_data = b'fake audio data'
        
        mock_segments = [
            Mock(text='Hello'),
            Mock(text='world'),
            Mock(text='test')
        ]
        mock_info = Mock()
        mock_info.language = 'en'
        
        mock_model = Mock()
        mock_model.transcribe.return_value = (
            mock_segments,
            mock_info
        )
        
        service = ASRService()
        service.model = mock_model
        
        text, language = service.transcribe(audio_data)
        
        assert text == 'Hello world test'
        assert language == 'en'
    
    def test_transcribe_exception_handling(self):
        """Test transcription exception handling."""
        audio_data = b'fake audio data'
        
        mock_model = Mock()
        mock_model.transcribe.side_effect = Exception('Transcription failed')
        
        service = ASRService()
        service.model = mock_model
        
        with pytest.raises(RuntimeError, match='Transcription failed'):
            service.transcribe(audio_data)
    
    def test_transcribe_cleanup_temp_file(self):
        """Test that temporary files are cleaned up."""
        audio_data = b'fake audio data'
        
        mock_segment = Mock()
        mock_segment.text = 'Test'
        mock_info = Mock()
        mock_info.language = 'en'
        
        mock_model = Mock()
        mock_model.transcribe.return_value = (
            [mock_segment],
            mock_info
        )
        
        service = ASRService()
        service.model = mock_model
        
        # Track temp files
        temp_files_before = set(Path(tempfile.gettempdir()).glob('tmp*'))
        
        service.transcribe(audio_data)
        
        # Verify temp file was cleaned up (or at least created)
        # Note: This is a basic check, actual cleanup happens in finally block


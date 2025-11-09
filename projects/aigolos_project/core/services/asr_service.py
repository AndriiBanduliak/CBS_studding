"""
ASR Service - Speech Recognition using faster-whisper.
"""

import logging
from typing import Optional, Tuple
from pathlib import Path
import tempfile
from django.conf import settings
from core.exceptions import ASRServiceError

logger = logging.getLogger('core')


class ASRService:
    """Service for speech recognition using faster-whisper."""
    
    def __init__(self):
        """Initialize ASR service."""
        self.model = None
        self._model_loaded = False
        # Lazy loading: model will be loaded on first use
    
    def _initialize_model(self):
        """Initialize the Whisper model (lazy loading)."""
        if self._model_loaded:
            return
        
        try:
            from faster_whisper import WhisperModel
            
            logger.info(f"Loading Whisper model: {settings.ASR_MODEL_NAME}")
            self.model = WhisperModel(
                settings.ASR_MODEL_NAME,
                device=settings.ASR_DEVICE,
                compute_type=settings.ASR_COMPUTE_TYPE
            )
            self._model_loaded = True
            logger.info("Whisper model loaded successfully")
        except ImportError:
            logger.warning("faster-whisper not installed. ASR functionality will be limited.")
            self.model = None
            self._model_loaded = True  # Mark as loaded to prevent retries
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}", exc_info=True)
            self.model = None
            self._model_loaded = True  # Mark as loaded to prevent retries
    
    def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Transcribe audio to text.
        
        Args:
            audio_data: Audio file bytes
            language: Optional language code
            
        Returns:
            Tuple of (transcribed_text, detected_language)
            
        Raises:
            ASRServiceError: If transcription fails
        """
        # Lazy load model on first use
        if not self._model_loaded:
            self._initialize_model()
        
        if self.model is None:
            raise ASRServiceError("ASR model is not available. Install faster-whisper.")
        
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name
            
            try:
                # Transcribe
                segments, info = self.model.transcribe(
                    tmp_path,
                    language=language,
                    beam_size=5
                )
                
                # Combine segments
                text = " ".join([segment.text for segment in segments])
                detected_language = info.language
                
                logger.info(f"Transcription completed. Language: {detected_language}")
                return text.strip(), detected_language
                
            finally:
                # Clean up temporary file
                Path(tmp_path).unlink(missing_ok=True)
                
        except ASRServiceError:
            raise
        except Exception as e:
            logger.error(f"Transcription failed: {e}", exc_info=True)
            raise ASRServiceError(f"Transcription failed: {e}")


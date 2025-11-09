"""
TTS Service - Text-to-Speech using Piper.
"""

import logging
from typing import Optional
from pathlib import Path
import tempfile
import subprocess
from django.conf import settings
from core.exceptions import TTSServiceError

logger = logging.getLogger('core')


class TTSService:
    """Service for text-to-speech using Piper."""
    
    def __init__(self):
        """Initialize TTS service."""
        self.voice_name = settings.TTS_VOICE_NAME
        self.model_path = settings.TTS_MODEL_PATH
        self._piper_available = self._check_piper()
    
    def _check_piper(self) -> bool:
        """Check if Piper is available."""
        try:
            result = subprocess.run(
                ["piper", "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("Piper TTS is available")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        logger.debug("Piper TTS not found. TTS functionality will be limited.")
        return False
    
    def synthesize(
        self,
        text: str,
        voice: Optional[str] = None
    ) -> bytes:
        """
        Synthesize text to speech.
        
        Args:
            text: Text to convert to speech
            voice: Optional voice name (overrides default)
            
        Returns:
            Audio data as bytes (WAV format)
            
        Raises:
            TTSServiceError: If synthesis fails
        """
        if not self._piper_available:
            raise TTSServiceError(
                "Piper TTS is not available. Please install Piper TTS from "
                "https://github.com/rhasspy/piper/releases and ensure it's in your PATH."
            )
        
        voice_name = voice or self.voice_name
        
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as text_file:
                text_file.write(text)
                text_path = text_file.name
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio_file:
                audio_path = audio_file.name
            
            try:
                # Run Piper TTS
                cmd = [
                    "piper",
                    "--model", voice_name,
                    "--output_file", audio_path
                ]
                
                if self.model_path:
                    cmd.extend(["--model_path", self.model_path])
                
                result = subprocess.run(
                    cmd,
                    input=text.encode(),
                    capture_output=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    raise TTSServiceError(f"Piper TTS failed: {result.stderr.decode()}")
                
                # Read generated audio
                with open(audio_path, "rb") as f:
                    audio_data = f.read()
                
                logger.info(f"TTS synthesis completed (audio size: {len(audio_data)} bytes)")
                return audio_data
                
            finally:
                # Clean up temporary files
                Path(text_path).unlink(missing_ok=True)
                Path(audio_path).unlink(missing_ok=True)
                
        except subprocess.TimeoutExpired:
            logger.error("TTS synthesis timed out", exc_info=True)
            raise TTSServiceError("TTS synthesis timed out")
        except TTSServiceError:
            raise
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}", exc_info=True)
            raise TTSServiceError(f"TTS synthesis failed: {e}")


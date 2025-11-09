"""
Custom validators for file uploads and security.
"""

import logging
import mimetypes
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger('core')


# Allowed audio MIME types
ALLOWED_AUDIO_MIME_TYPES = {
    'audio/wav',
    'audio/wave',
    'audio/x-wav',
    'audio/mpeg',
    'audio/mp3',
    'audio/x-mpeg-3',
    'audio/flac',
    'audio/x-flac',
    'audio/ogg',
    'audio/webm',
    'audio/mp4',
    'audio/x-m4a',
}

# Allowed audio file extensions
ALLOWED_AUDIO_EXTENSIONS = {
    '.wav', '.wave',
    '.mp3', '.mpeg',
    '.flac',
    '.ogg',
    '.webm',
    '.m4a', '.mp4',
}


def validate_audio_file(file):
    """
    Validate that uploaded file is a valid audio file.
    
    Args:
        file: Django UploadedFile object
        
    Raises:
        ValidationError: If file is not a valid audio file
    """
    # Check file extension
    file_name = file.name.lower()
    file_extension = None
    for ext in ALLOWED_AUDIO_EXTENSIONS:
        if file_name.endswith(ext):
            file_extension = ext
            break
    
    if not file_extension:
        raise ValidationError(
            _('Invalid file type. Allowed formats: WAV, MP3, FLAC, OGG, WEBM, M4A')
        )
    
    # Check MIME type
    # First try to get from file.content_type
    mime_type = file.content_type
    
    # If content_type is not reliable, try to detect from file content
    if not mime_type or mime_type not in ALLOWED_AUDIO_MIME_TYPES:
        # Try to detect MIME type from file extension
        detected_mime, _ = mimetypes.guess_type(file_name)
        if detected_mime:
            mime_type = detected_mime
    
    # Additional check: read file header (magic bytes)
    try:
        file.seek(0)
        header = file.read(12)
        file.seek(0)  # Reset file pointer
        
        # Check magic bytes for common audio formats
        is_valid_audio = False
        
        # WAV: RIFF...WAVE
        if header.startswith(b'RIFF') and b'WAVE' in header[:12]:
            is_valid_audio = True
        # MP3: ID3 tag or MPEG header
        elif header.startswith(b'ID3') or header[:2] == b'\xff\xfb':
            is_valid_audio = True
        # FLAC: fLaC
        elif header.startswith(b'fLaC'):
            is_valid_audio = True
        # OGG: OggS
        elif header.startswith(b'OggS'):
            is_valid_audio = True
        # WebM: starts with EBML
        elif header.startswith(b'\x1a\x45\xdf\xa3'):
            is_valid_audio = True
        # M4A/MP4: ftyp box
        elif b'ftyp' in header[:12]:
            is_valid_audio = True
        
        if not is_valid_audio:
            logger.warning(f"File {file_name} failed magic bytes validation")
            raise ValidationError(
                _('File does not appear to be a valid audio file. Please upload a valid audio file.')
            )
    except Exception as e:
        logger.error(f"Error validating audio file: {e}")
        raise ValidationError(
            _('Error validating file. Please ensure it is a valid audio file.')
        )
    
    # Final MIME type check
    if mime_type and mime_type not in ALLOWED_AUDIO_MIME_TYPES:
        logger.warning(f"File {file_name} has unsupported MIME type: {mime_type}")
        raise ValidationError(
            _('Unsupported audio format. Allowed formats: WAV, MP3, FLAC, OGG, WEBM, M4A')
        )


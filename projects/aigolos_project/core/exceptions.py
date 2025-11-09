"""
Custom exceptions for AIGolos services.
"""


class AIGolosException(Exception):
    """Base exception for AIGolos."""
    pass


class ASRServiceError(AIGolosException):
    """Exception raised by ASR service."""
    pass


class LLMServiceError(AIGolosException):
    """Exception raised by LLM service."""
    pass


class TTSServiceError(AIGolosException):
    """Exception raised by TTS service."""
    pass


class ValidationError(AIGolosException):
    """Exception for validation errors."""
    pass


"""
Custom throttle classes for rate limiting.
"""

from rest_framework.throttling import UserRateThrottle


class ASRThrottle(UserRateThrottle):
    """Throttle for ASR endpoint (resource-intensive)."""
    rate = '20/hour'


class LLMThrottle(UserRateThrottle):
    """Throttle for LLM endpoint."""
    rate = '100/hour'


class TTSThrottle(UserRateThrottle):
    """Throttle for TTS endpoint."""
    rate = '50/hour'


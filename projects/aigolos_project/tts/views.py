"""
Views for TTS app.
"""

import logging
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from django.core.files.base import ContentFile
from core.services import tts_service
from core.throttles import TTSThrottle
from core.exceptions import TTSServiceError
from core.view_services import TTSViewService
from core.base_views import BaseAPIViewMixin
from .models import Synthesis
from .serializers import TTSRequestSerializer

logger = logging.getLogger('tts')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@throttle_classes([TTSThrottle])
def synthesize_view(request):
    """
    Synthesize text to speech.
    
    Rate limited to 50 requests per hour per user.
    """
    try:
        # Validate request data using serializer
        request_serializer = TTSRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            return Response(
                request_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        text = request_serializer.validated_data['text']
        voice = request_serializer.validated_data.get('voice')
        
        # Use service layer for business logic
        synthesis = TTSViewService.synthesize_text(
            user=request.user,
            text=text,
            voice=voice
        )
        
        # Return audio file
        from django.http import FileResponse
        return FileResponse(
            synthesis.audio_file.open('rb'),
            content_type='audio/wav',
            as_attachment=True,
            filename='synthesis.wav'
        )
        
    except TTSServiceError as e:
        return BaseAPIViewMixin().handle_service_error(e, "TTS error")
    except Exception as e:
        return BaseAPIViewMixin().handle_generic_error(e, "Internal server error")


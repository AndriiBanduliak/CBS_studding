"""
Views for ASR app.
"""

import logging
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.core.cache import cache
from core.services import asr_service
from core.validators import validate_audio_file
from core.throttles import ASRThrottle
from core.exceptions import ASRServiceError
from core.view_services import ASRViewService
from core.base_views import BaseAPIViewMixin
from core.filters import TranscriptionFilter
from .models import Transcription
from .serializers import TranscriptionSerializer, TranscriptionRequestSerializer

logger = logging.getLogger('asr')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@throttle_classes([ASRThrottle])
def transcribe_view(request):
    """
    Transcribe audio file.
    
    Rate limited to 20 requests per hour per user.
    """
    try:
        if 'audio' not in request.FILES:
            return Response(
                {'error': 'No audio file provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        audio_file = request.FILES['audio']
        
        # Validate request data using serializer
        request_serializer = TranscriptionRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            return Response(
                request_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        language = request_serializer.validated_data.get('language')
        
        # Validate file type (MIME type and magic bytes)
        try:
            validate_audio_file(audio_file)
        except ValidationError as e:
            logger.warning(f"Invalid audio file uploaded by {request.user.username}: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check file size
        from django.conf import settings
        if audio_file.size > settings.MAX_AUDIO_SIZE:
            return Response(
                {'error': f'File too large. Maximum size: {settings.MAX_AUDIO_SIZE} bytes'},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            )
        
        # Use service layer for business logic
        transcription = ASRViewService.transcribe_audio(
            user=request.user,
            audio_file=audio_file,
            language=language
        )
        
        serializer = TranscriptionSerializer(transcription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except ASRServiceError as e:
        return BaseAPIViewMixin().handle_service_error(e, "Transcription error")
    except ValidationError as e:
        return BaseAPIViewMixin().handle_validation_error({'error': str(e)})
    except Exception as e:
        return BaseAPIViewMixin().handle_generic_error(e, "Internal server error")


class TranscriptionListView(generics.ListAPIView):
    """List user transcriptions with filtering, searching, and sorting."""
    serializer_class = TranscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ASRThrottle]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TranscriptionFilter
    search_fields = ['text', 'language']
    ordering_fields = ['created_at', 'language']
    ordering = ['-created_at']  # Default ordering
    
    def get_queryset(self):
        """Get user's transcriptions."""
        # Use filter() with user to prevent SQL injection - Django ORM handles parameterization
        # Use select_related for user to reduce queries
        # Pagination is handled by DRF (configured in settings: PAGE_SIZE=20)
        return Transcription.objects.filter(user=self.request.user).select_related('user')


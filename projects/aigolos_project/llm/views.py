"""
Views for LLM app.
"""

import logging
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from core.services import llm_service
from core.throttles import LLMThrottle
from core.exceptions import LLMServiceError
from core.view_services import LLMViewService
from core.base_views import BaseAPIViewMixin
from core.filters import ConversationFilter
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, ChatRequestSerializer

logger = logging.getLogger('llm')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@throttle_classes([LLMThrottle])
def chat_view(request):
    """
    Chat with LLM.
    
    Rate limited to 100 requests per hour per user.
    """
    try:
        # Validate request data using serializer
        request_serializer = ChatRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            return Response(
                request_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        message_text = request_serializer.validated_data['message']
        conversation_id = request_serializer.validated_data.get('conversation_id')
        
        # Use service layer for business logic
        conversation, user_message, ai_message = LLMViewService.process_chat_message(
            user=request.user,
            message_text=message_text,
            conversation_id=conversation_id
        )
        
        return Response({
            'conversation_id': conversation.id,
            'user_message': MessageSerializer(user_message).data,
            'ai_message': MessageSerializer(ai_message).data,
        }, status=status.HTTP_201_CREATED)
        
    except Conversation.DoesNotExist:
        return Response(
            {'error': 'Conversation not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    except LLMServiceError as e:
        return BaseAPIViewMixin().handle_service_error(e, "Chat error")
    except Exception as e:
        return BaseAPIViewMixin().handle_generic_error(e, "Internal server error")


class ConversationListView(generics.ListAPIView):
    """List user conversations with filtering, searching, and sorting."""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [LLMThrottle]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ConversationFilter
    search_fields = ['title', 'messages__content']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-updated_at']  # Default ordering
    
    def get_queryset(self):
        """Get user's conversations."""
        # Django ORM filter() automatically parameterizes queries - prevents SQL injection
        # Use select_related for user and prefetch_related for messages to optimize queries
        # Pagination is handled by DRF (configured in settings: PAGE_SIZE=20)
        return Conversation.objects.filter(user=self.request.user).select_related('user').prefetch_related('messages')


class ConversationDetailView(generics.RetrieveAPIView):
    """Get conversation details."""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [LLMThrottle]
    
    def get_queryset(self):
        """Get user's conversations."""
        # Django ORM filter() automatically parameterizes queries - prevents SQL injection
        # Use select_related for user and prefetch_related for messages to optimize queries
        return Conversation.objects.filter(user=self.request.user).select_related('user').prefetch_related('messages')


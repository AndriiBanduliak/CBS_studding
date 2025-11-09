"""
Views for accounts app.
"""

import logging
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import User
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer

logger = logging.getLogger('accounts')


def register_page(request):
    """Registration page."""
    return render(request, 'accounts/register.html')


def login_page(request):
    """Login page."""
    return render(request, 'accounts/login.html')


class RegisterView(generics.CreateAPIView):
    """User registration API view."""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        """Create new user."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        logger.info(f"User registered: {user.username}")
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """User login API view."""
    serializer = UserLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        logger.info(f"User logged in: {user.username}")
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })
    else:
        logger.warning(f"Failed login attempt for username: {username}")
        return Response(
            {'error': 'Invalid credentials.'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """User logout API view."""
    try:
        request.user.auth_token.delete()
    except Exception:
        pass
    logout(request)
    logger.info(f"User logged out: {request.user.username}")
    return Response({'message': 'Logged out successfully.'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile_view(request):
    """Get user profile."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_profile_view(request):
    """Update user profile."""
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        logger.info(f"Profile updated for user: {request.user.username}")
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def stats_view(request):
    """
    Get user statistics.
    
    Returns:
        - total_transcriptions: Total number of transcriptions
        - total_conversations: Total number of conversations
        - total_syntheses: Total number of syntheses
        - recent_activity: Recent activity summary
    """
    from asr.models import Transcription
    from llm.models import Conversation
    from tts.models import Synthesis
    from django.utils import timezone
    from datetime import timedelta
    
    user = request.user
    
    # Count totals
    total_transcriptions = Transcription.objects.filter(user=user).count()
    total_conversations = Conversation.objects.filter(user=user).count()
    total_syntheses = Synthesis.objects.filter(user=user).count()
    
    # Recent activity (last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_transcriptions = Transcription.objects.filter(
        user=user,
        created_at__gte=seven_days_ago
    ).count()
    recent_conversations = Conversation.objects.filter(
        user=user,
        created_at__gte=seven_days_ago
    ).count()
    recent_syntheses = Synthesis.objects.filter(
        user=user,
        created_at__gte=seven_days_ago
    ).count()
    
    return Response({
        'total_transcriptions': total_transcriptions,
        'total_conversations': total_conversations,
        'total_syntheses': total_syntheses,
        'recent_activity': {
            'transcriptions': recent_transcriptions,
            'conversations': recent_conversations,
            'syntheses': recent_syntheses,
            'period_days': 7
        }
    })

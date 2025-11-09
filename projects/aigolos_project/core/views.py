"""
Views for core app.
"""

from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions


def index_view(request):
    """Main web interface."""
    # Allow both authenticated and anonymous users
    return render(request, 'core/index.html')


@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Allow unauthenticated access for monitoring
def health_view(request):
    """Health check endpoint."""
    response_data = {
        'status': 'healthy',
        'version': '2.0.0',
    }
    # Include user info if authenticated, but don't require it
    if request.user.is_authenticated:
        response_data['user'] = request.user.username
    return Response(response_data)


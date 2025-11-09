"""
Password reset functionality.
"""

import logging
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from .models import User

logger = logging.getLogger('accounts')


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_request(request):
    """Request password reset."""
    email = request.data.get('email', '').strip()
    
    if not email:
        return Response(
            {'error': 'Email is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Don't reveal if email exists for security
        logger.warning(f"Password reset requested for non-existent email: {email}")
        return Response(
            {'message': 'If an account exists with this email, a password reset link has been sent.'},
            status=status.HTTP_200_OK
        )
    
    # Generate token
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Create reset link
    reset_link = f"{request.scheme}://{request.get_host()}/api/auth/password-reset/confirm/?uid={uid}&token={token}"
    
    # Send email (in production, use proper email backend)
    try:
        send_mail(
            subject='Password Reset Request - AIGolos',
            message=f'Click the following link to reset your password: {reset_link}',
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@aigolos.com',
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info(f"Password reset email sent to: {email}")
    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
        return Response(
            {'error': 'Failed to send password reset email. Please try again later.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return Response(
        {'message': 'If an account exists with this email, a password reset link has been sent.'},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_confirm(request):
    """Confirm password reset."""
    uid = request.data.get('uid', '')
    token = request.data.get('token', '')
    new_password = request.data.get('password', '')
    
    if not all([uid, token, new_password]):
        return Response(
            {'error': 'UID, token, and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(new_password) < 8:
        return Response(
            {'error': 'Password must be at least 8 characters long.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        from django.utils.encoding import force_str
        from django.utils.http import urlsafe_base64_decode
        
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {'error': 'Invalid reset link.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify token
    if not default_token_generator.check_token(user, token):
        return Response(
            {'error': 'Invalid or expired reset token.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Set new password
    user.set_password(new_password)
    user.save()
    
    logger.info(f"Password reset successful for user: {user.username}")
    
    return Response(
        {'message': 'Password has been reset successfully.'},
        status=status.HTTP_200_OK
    )


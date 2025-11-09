"""
Base view classes for common functionality.
"""

from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('core')


class BaseAPIViewMixin:
    """Base mixin for API views with common error handling."""
    
    def handle_service_error(self, error, error_message: str = "Service error"):
        """Handle service errors consistently."""
        logger.error(f"{error_message}: {error}", exc_info=True)
        return Response(
            {'error': str(error)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    def handle_validation_error(self, errors):
        """Handle validation errors consistently."""
        return Response(
            errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def handle_generic_error(self, error, error_message: str = "Internal server error"):
        """Handle generic errors consistently."""
        logger.error(f"{error_message}: {error}", exc_info=True)
        return Response(
            {'error': error_message},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


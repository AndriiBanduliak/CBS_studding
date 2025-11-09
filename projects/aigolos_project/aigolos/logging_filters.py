"""
Logging filters to prevent encoding errors.
"""

import logging


class IgnoreEncodingErrorsFilter(logging.Filter):
    """
    Filter that ignores log records that would cause encoding errors.
    """
    
    def filter(self, record):
        """Filter out records with problematic characters or bad requests."""
        try:
            msg = str(record.getMessage())
            
            # Skip bad request version errors (HTTPS attempts, port scanners)
            if 'Bad request' in msg or 'Bad request version' in msg:
                return False
            if 'HTTPS' in msg and 'only supports HTTP' in msg:
                return False
            if 'code 400, message' in msg:
                return False
            
            # Try to encode the message to check if it's safe
            try:
                msg.encode('cp1251')  # Try Windows default encoding
                return True
            except (UnicodeEncodeError, UnicodeDecodeError):
                # If encoding fails, skip this log entry
                return False
        except Exception:
            # For any other error, allow the log
            return True


class DjangoServerFilter(logging.Filter):
    """
    Filter for django.server that filters out HTTP request logs
    but allows all other messages (including server startup).
    """
    
    def filter(self, record):
        """Filter out HTTP request logs, allow everything else."""
        try:
            msg = str(record.getMessage())
            
            # Filter out HTTP request logs (they cause encoding issues)
            # But allow important messages
            if 'GET /' in msg or 'POST /' in msg or 'PUT /' in msg or 'DELETE /' in msg:
                # Check if it's a request log (has status code)
                if any(code in msg for code in ['200', '201', '301', '302', '304', '400', '401', '403', '404', '500']):
                    return False
            
            # Filter out problematic messages
            if 'Bad request' in msg or 'Bad request version' in msg:
                return False
            if 'HTTPS' in msg and 'only supports HTTP' in msg:
                return False
            if 'code 400, message' in msg:
                return False
            
            # Allow everything else (including "Starting development server")
            return True
        except Exception:
            # For any error, allow the log
            return True


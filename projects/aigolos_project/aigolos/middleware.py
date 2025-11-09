"""
Custom middleware for AIGolos.
"""

import logging
import time
import uuid
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger('aigolos')
security_logger = logging.getLogger('security')


class LoggingMiddleware(MiddlewareMixin):
    """Middleware for logging requests and errors."""
    
    def process_request(self, request):
        """Log request start time and add correlation ID."""
        request._start_time = time.time()
        # Add correlation ID for request tracking
        request.correlation_id = str(uuid.uuid4())[:8]
    
    def process_response(self, request, response):
        """Log request completion."""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            correlation_id = getattr(request, 'correlation_id', 'N/A')
            user_info = request.user if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous'
            logger.info(
                f"[{correlation_id}] {request.method} {request.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.3f}s - "
                f"User: {user_info}",
                extra={'correlation_id': correlation_id}
            )
            
            # Record metrics
            try:
                from core.metrics import MetricsCollector
                MetricsCollector.record_api_request(
                    request.path,
                    request.method,
                    response.status_code,
                    duration
                )
            except Exception:
                pass  # Don't fail if metrics fail
            
            # Log suspicious activity
            self._check_suspicious_activity(request, response)
        return response
    
    def process_exception(self, request, exception):
        """Log exceptions."""
        correlation_id = getattr(request, 'correlation_id', 'N/A')
        logger.error(
            f"[{correlation_id}] Exception in {request.method} {request.path}: {str(exception)}",
            exc_info=True,
            extra={'correlation_id': correlation_id}
        )
        return None
    
    def _check_suspicious_activity(self, request, response):
        """Check and log suspicious activity."""
        ip_address = self._get_client_ip(request)
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        
        # Check for failed authentication attempts
        if response.status_code == 401 or response.status_code == 403:
            cache_key = f'failed_auth_{ip_address}'
            failed_count = cache.get(cache_key, 0) + 1
            cache.set(cache_key, failed_count, 3600)  # 1 hour
            
            if failed_count >= 5:
                correlation_id = getattr(request, 'correlation_id', 'N/A')
                security_logger.warning(
                    f"[{correlation_id}] Suspicious activity: Multiple failed auth attempts - "
                    f"IP: {ip_address}, Count: {failed_count}, Path: {request.path}",
                    extra={'correlation_id': correlation_id, 'ip_address': ip_address}
                )
        
        # Check for rate limiting violations
        if response.status_code == 429:
            correlation_id = getattr(request, 'correlation_id', 'N/A')
            security_logger.warning(
                f"[{correlation_id}] Rate limit exceeded - IP: {ip_address}, "
                f"User: {user.username if user else 'Anonymous'}, Path: {request.path}",
                extra={'correlation_id': correlation_id, 'ip_address': ip_address}
            )
        
        # Check for invalid file uploads
        if response.status_code == 400 and 'audio' in request.path:
            security_logger.warning(
                f"Invalid file upload attempt - IP: {ip_address}, "
                f"User: {user.username if user else 'Anonymous'}"
            )
        
        # Check for SQL injection patterns (basic check)
        suspicious_patterns = ['union select', 'drop table', ';--', 'exec(', 'script>']
        query_string = str(request.GET) + str(request.POST)
        for pattern in suspicious_patterns:
            if pattern.lower() in query_string.lower():
                security_logger.error(
                    f"Potential SQL injection attempt - IP: {ip_address}, "
                    f"User: {user.username if user else 'Anonymous'}, "
                    f"Pattern: {pattern}, Path: {request.path}"
                )
                break
    
    def _get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Middleware for adding security headers including CSP."""
    
    def process_response(self, request, response):
        """Add security headers to response."""
        from django.conf import settings
        
        # Content Security Policy
        if not settings.DEBUG:
            csp_parts = [
                f"default-src {settings.CSP_DEFAULT_SRC}",
                f"script-src {settings.CSP_SCRIPT_SRC}",
                f"style-src {settings.CSP_STYLE_SRC}",
                f"img-src {settings.CSP_IMG_SRC}",
                f"font-src {settings.CSP_FONT_SRC}",
                f"connect-src {settings.CSP_CONNECT_SRC}",
                "frame-ancestors 'none'",
            ]
            response['Content-Security-Policy'] = '; '.join(csp_parts)
        
        return response


class CompressionMiddleware(MiddlewareMixin):
    """Middleware for compressing responses."""
    
    def process_response(self, request, response):
        """Compress response if applicable."""
        # Skip compression if already compressed or if Content-Encoding is set
        if response.get('Content-Encoding'):
            return response
        
        # Only compress text-based content
        content_type = response.get('Content-Type', '')
        if any(ct in content_type for ct in ['text/html', 'text/css', 'application/javascript', 'application/json']):
            # Check if client supports gzip
            accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
            if 'gzip' in accept_encoding:
                try:
                    content = response.content
                    if len(content) > 200:  # Only compress if > 200 bytes
                        import gzip
                        compressed_content = gzip.compress(content)
                        response.content = compressed_content
                        response['Content-Encoding'] = 'gzip'
                        response['Content-Length'] = str(len(compressed_content))
                except (AttributeError, TypeError):
                    # Skip compression if content is not bytes
                    pass
        
        return response


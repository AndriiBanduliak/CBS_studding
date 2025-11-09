"""
Metrics collection for monitoring.
"""

import logging
import time
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from typing import Dict, Any

logger = logging.getLogger('core')


class MetricsCollector:
    """Collect application metrics."""
    
    @staticmethod
    def record_api_request(endpoint: str, method: str, status_code: int, duration: float):
        """Record API request metrics."""
        cache_key = f'metrics:api:{endpoint}:{method}'
        data = cache.get(cache_key, {'count': 0, 'total_duration': 0, 'errors': 0})
        data['count'] += 1
        data['total_duration'] += duration
        if status_code >= 400:
            data['errors'] += 1
        cache.set(cache_key, data, 3600)  # 1 hour
    
    @staticmethod
    def get_api_metrics(endpoint: str = None, method: str = None) -> Dict[str, Any]:
        """Get API metrics."""
        if endpoint and method:
            cache_key = f'metrics:api:{endpoint}:{method}'
            data = cache.get(cache_key, {})
            if data:
                return {
                    'count': data.get('count', 0),
                    'avg_duration': data.get('total_duration', 0) / max(data.get('count', 1), 1),
                    'errors': data.get('errors', 0),
                    'error_rate': data.get('errors', 0) / max(data.get('count', 1), 1)
                }
        return {}
    
    @staticmethod
    def record_user_activity(user_id: int, activity_type: str):
        """Record user activity."""
        today = timezone.now().date()
        cache_key = f'metrics:user:{user_id}:{today}:{activity_type}'
        count = cache.get(cache_key, 0) + 1
        cache.set(cache_key, count, 86400)  # 24 hours
    
    @staticmethod
    def get_user_stats(user_id: int) -> Dict[str, Any]:
        """Get user statistics for today."""
        today = timezone.now().date()
        return {
            'transcriptions': cache.get(f'metrics:user:{user_id}:{today}:transcription', 0),
            'conversations': cache.get(f'metrics:user:{user_id}:{today}:conversation', 0),
            'syntheses': cache.get(f'metrics:user:{user_id}:{today}:synthesis', 0),
        }


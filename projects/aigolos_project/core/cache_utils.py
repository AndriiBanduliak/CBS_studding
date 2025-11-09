"""
Cache utilities for frequently accessed data.
"""

from django.core.cache import cache
from django.conf import settings
import hashlib
import json


def get_cache_key(prefix, *args, **kwargs):
    """Generate cache key from prefix and arguments."""
    key_parts = [prefix] + [str(arg) for arg in args]
    if kwargs:
        key_parts.append(json.dumps(kwargs, sort_keys=True))
    key_string = ':'.join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def cache_user_data(user_id, data, timeout=300):
    """Cache user-specific data."""
    cache_key = f'user_data_{user_id}'
    cache.set(cache_key, data, timeout)
    return data


def get_cached_user_data(user_id):
    """Get cached user data."""
    cache_key = f'user_data_{user_id}'
    return cache.get(cache_key)


def cache_transcription_list(user_id, transcriptions, timeout=300):
    """Cache user's transcription list."""
    cache_key = f'transcriptions_{user_id}'
    cache.set(cache_key, transcriptions, timeout)
    return transcriptions


def get_cached_transcription_list(user_id):
    """Get cached transcription list."""
    cache_key = f'transcriptions_{user_id}'
    return cache.get(cache_key)


def cache_conversation_list(user_id, conversations, timeout=300):
    """Cache user's conversation list."""
    cache_key = f'conversations_{user_id}'
    cache.set(cache_key, conversations, timeout)
    return conversations


def get_cached_conversation_list(user_id):
    """Get cached conversation list."""
    cache_key = f'conversations_{user_id}'
    return cache.get(cache_key)


def invalidate_user_cache(user_id):
    """Invalidate all cache for a user."""
    cache_keys = [
        f'user_data_{user_id}',
        f'transcriptions_{user_id}',
        f'conversations_{user_id}',
    ]
    for key in cache_keys:
        cache.delete(key)


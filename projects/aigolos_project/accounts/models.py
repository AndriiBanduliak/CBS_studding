"""
User models for accounts app.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
import logging

logger = logging.getLogger('accounts')


class User(AbstractUser):
    """Custom user model."""
    
    email = models.EmailField(unique=True, blank=False)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_premium = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email'], name='user_email_idx'),
            models.Index(fields=['username'], name='user_username_idx'),
        ]
    
    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        """Override save to log user creation."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"New user created: {self.username}")


class UserSession(models.Model):
    """Track user sessions."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_sessions'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.username} - {self.ip_address}"


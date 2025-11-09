"""
Tests for User model.
"""

import pytest
from django.contrib.auth import get_user_model
from accounts.models import UserSession
from tests.conftest import UserFactory

User = get_user_model()


class TestUser:
    """Test cases for User model."""
    
    def test_user_creation(self, db):
        """Test user creation."""
        user = UserFactory()
        assert user.pk is not None
        assert user.username is not None
        assert user.email is not None
        assert user.is_active is True
    
    def test_user_str(self, db):
        """Test user string representation."""
        user = UserFactory(username='testuser')
        assert str(user) == 'testuser'
    
    def test_user_email_unique(self, db):
        """Test that email must be unique."""
        UserFactory(email='test@example.com')
        
        with pytest.raises(Exception):  # IntegrityError or ValidationError
            UserFactory(email='test@example.com')
    
    def test_user_avatar_optional(self, db):
        """Test that avatar is optional."""
        user = UserFactory(avatar=None)
        # ImageField returns ImageFieldFile object even when None
        assert not user.avatar or user.avatar.name == ''
    
    def test_user_is_premium_default(self, db):
        """Test that is_premium defaults to False."""
        user = UserFactory()
        assert user.is_premium is False
    
    def test_user_timestamps(self, db):
        """Test that created_at and updated_at are set."""
        user = UserFactory()
        assert user.created_at is not None
        assert user.updated_at is not None


class TestUserSession:
    """Test cases for UserSession model."""
    
    def test_session_creation(self, db, user):
        """Test session creation."""
        session = UserSession.objects.create(
            user=user,
            session_key='test_session_key',
            ip_address='127.0.0.1',
            user_agent='Test Agent'
        )
        assert session.pk is not None
        assert session.user == user
        assert session.is_active is True
    
    def test_session_str(self, db, user):
        """Test session string representation."""
        session = UserSession.objects.create(
            user=user,
            session_key='test_key',
            ip_address='192.168.1.1',
            user_agent='Test'
        )
        assert str(session) == f'{user.username} - 192.168.1.1'
    
    def test_session_ordering(self, db, user):
        """Test that sessions are ordered by last_activity descending."""
        session1 = UserSession.objects.create(
            user=user,
            session_key='key1',
            ip_address='127.0.0.1',
            user_agent='Test'
        )
        session2 = UserSession.objects.create(
            user=user,
            session_key='key2',
            ip_address='127.0.0.1',
            user_agent='Test'
        )
        
        sessions = list(UserSession.objects.all())
        # Most recent should be first
        assert sessions[0].last_activity >= sessions[1].last_activity


"""
Tests for accounts serializers.
"""

import pytest
from rest_framework.exceptions import ValidationError
from accounts.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer
)
from tests.conftest import UserFactory


class TestUserRegistrationSerializer:
    """Test cases for UserRegistrationSerializer."""
    
    def test_valid_registration(self, db):
        """Test valid user registration."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        serializer = UserRegistrationSerializer(data=data)
        assert serializer.is_valid()
        
        user = serializer.save()
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.check_password('testpass123')
    
    def test_password_mismatch(self, db):
        """Test password mismatch validation."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'differentpass'
        }
        serializer = UserRegistrationSerializer(data=data)
        
        assert not serializer.is_valid()
        assert 'password' in serializer.errors
    
    def test_password_too_short(self, db):
        """Test password minimum length validation."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'short',
            'password_confirm': 'short'
        }
        serializer = UserRegistrationSerializer(data=data)
        
        assert not serializer.is_valid()


class TestUserLoginSerializer:
    """Test cases for UserLoginSerializer."""
    
    def test_valid_login(self, db):
        """Test valid user login."""
        user = UserFactory(password='testpass123')
        
        data = {
            'username': user.username,
            'password': 'testpass123'
        }
        serializer = UserLoginSerializer(data=data)
        
        assert serializer.is_valid()
        assert serializer.validated_data['user'] == user
    
    def test_invalid_credentials(self, db):
        """Test invalid credentials."""
        UserFactory(username='testuser', password='correctpass')
        
        data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        serializer = UserLoginSerializer(data=data)
        
        assert not serializer.is_valid()
    
    def test_missing_fields(self, db):
        """Test missing required fields."""
        data = {'username': 'testuser'}
        serializer = UserLoginSerializer(data=data)
        
        assert not serializer.is_valid()


class TestUserSerializer:
    """Test cases for UserSerializer."""
    
    def test_serialize_user(self, db):
        """Test user serialization."""
        user = UserFactory(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        
        serializer = UserSerializer(user)
        data = serializer.data
        
        assert data['username'] == 'testuser'
        assert data['email'] == 'test@example.com'
        assert data['first_name'] == 'Test'
        assert 'id' in data
        assert 'date_joined' in data


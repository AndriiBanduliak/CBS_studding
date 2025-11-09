"""
Tests for Conversation and Message models.
"""

import pytest
from llm.models import Conversation, Message
from tests.conftest import UserFactory


class TestConversation:
    """Test cases for Conversation model."""
    
    def test_conversation_creation(self, db):
        """Test conversation creation."""
        user = UserFactory()
        conversation = Conversation.objects.create(
            user=user,
            title='Test Conversation'
        )
        
        assert conversation.pk is not None
        assert conversation.user == user
        assert conversation.title == 'Test Conversation'
    
    def test_conversation_str(self, db):
        """Test conversation string representation."""
        user = UserFactory()
        conversation = Conversation.objects.create(
            user=user,
            title='My Chat'
        )
        assert str(conversation) == f'{user.username} - My Chat'
    
    def test_conversation_untitled(self, db):
        """Test conversation with empty title."""
        user = UserFactory()
        conversation = Conversation.objects.create(
            user=user,
            title=''
        )
        assert 'Untitled' in str(conversation)
    
    def test_conversation_ordering(self, db):
        """Test that conversations are ordered by updated_at descending."""
        user = UserFactory()
        
        conv1 = Conversation.objects.create(user=user, title='First')
        conv2 = Conversation.objects.create(user=user, title='Second')
        
        conversations = list(Conversation.objects.all())
        assert conversations[0].updated_at >= conversations[1].updated_at
    
    def test_conversation_timestamps(self, db):
        """Test that timestamps are set."""
        user = UserFactory()
        conversation = Conversation.objects.create(user=user, title='Test')
        
        assert conversation.created_at is not None
        assert conversation.updated_at is not None


class TestMessage:
    """Test cases for Message model."""
    
    def test_message_creation(self, db):
        """Test message creation."""
        user = UserFactory()
        conversation = Conversation.objects.create(user=user, title='Test')
        
        message = Message.objects.create(
            conversation=conversation,
            role='user',
            content='Hello'
        )
        
        assert message.pk is not None
        assert message.conversation == conversation
        assert message.role == 'user'
        assert message.content == 'Hello'
    
    def test_message_str(self, db):
        """Test message string representation."""
        user = UserFactory()
        conversation = Conversation.objects.create(user=user, title='Test')
        
        message = Message.objects.create(
            conversation=conversation,
            role='user',
            content='Hello world'
        )
        
        assert message.role in str(message)
        assert 'Hello' in str(message)
    
    def test_message_ordering(self, db):
        """Test that messages are ordered by created_at ascending."""
        user = UserFactory()
        conversation = Conversation.objects.create(user=user, title='Test')
        
        msg1 = Message.objects.create(
            conversation=conversation,
            role='user',
            content='First'
        )
        msg2 = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content='Second'
        )
        
        messages = list(Message.objects.all())
        assert messages[0].created_at <= messages[1].created_at
    
    def test_message_role_choices(self, db):
        """Test message role choices."""
        user = UserFactory()
        conversation = Conversation.objects.create(user=user, title='Test')
        
        # Valid roles
        user_msg = Message.objects.create(
            conversation=conversation,
            role='user',
            content='Test'
        )
        assistant_msg = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content='Test'
        )
        
        assert user_msg.role == 'user'
        assert assistant_msg.role == 'assistant'
    
    def test_message_cascade_delete(self, db):
        """Test that messages are deleted when conversation is deleted."""
        user = UserFactory()
        conversation = Conversation.objects.create(user=user, title='Test')
        
        message = Message.objects.create(
            conversation=conversation,
            role='user',
            content='Test'
        )
        message_id = message.pk
        
        conversation.delete()
        
        assert not Message.objects.filter(pk=message_id).exists()


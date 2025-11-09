"""
Serializers for LLM app.
"""

from rest_framework import serializers
from .models import Conversation, Message


class ChatRequestSerializer(serializers.Serializer):
    """Serializer for chat request validation."""
    
    message = serializers.CharField(
        max_length=5000,
        min_length=1,
        required=True,
        help_text="User message (1-5000 characters)"
    )
    conversation_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Optional conversation ID to continue existing conversation"
    )
    
    def validate_message(self, value):
        """Validate message content."""
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty.")
        if len(value.strip()) > 5000:
            raise serializers.ValidationError("Message is too long. Maximum 5000 characters.")
        return value.strip()


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model."""
    
    class Meta:
        model = Message
        fields = ('id', 'role', 'content', 'created_at')
        read_only_fields = ('id', 'created_at', 'role', 'content')


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model."""
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ('id', 'title', 'messages', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


"""
Serializers for ASR app.
"""

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Transcription


class TranscriptionRequestSerializer(serializers.Serializer):
    """Serializer for transcription request validation."""
    
    language = serializers.CharField(
        max_length=10,
        required=False,
        allow_blank=True,
        help_text="Optional language code (e.g., 'en', 'ru', 'de')"
    )
    
    def validate_language(self, value):
        """Validate language code format."""
        if value and len(value) > 10:
            raise serializers.ValidationError("Language code must be 10 characters or less.")
        return value.lower() if value else value


class TranscriptionSerializer(serializers.ModelSerializer):
    """Serializer for Transcription model."""
    
    class Meta:
        model = Transcription
        fields = ('id', 'text', 'language', 'created_at')
        read_only_fields = ('id', 'created_at')


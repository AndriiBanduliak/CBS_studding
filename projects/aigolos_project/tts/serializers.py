"""
Serializers for TTS app.
"""

from rest_framework import serializers
from .models import Synthesis


class TTSRequestSerializer(serializers.Serializer):
    """Serializer for TTS request validation."""
    
    text = serializers.CharField(
        max_length=5000,
        min_length=1,
        required=True,
        help_text="Text to synthesize (1-5000 characters)"
    )
    voice = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Optional voice name (e.g., 'en_US/amy/medium')"
    )
    
    def validate_text(self, value):
        """Validate text content."""
        if not value.strip():
            raise serializers.ValidationError("Text cannot be empty.")
        if len(value.strip()) > 5000:
            raise serializers.ValidationError("Text is too long. Maximum 5000 characters.")
        return value.strip()


class SynthesisSerializer(serializers.ModelSerializer):
    """Serializer for Synthesis model."""
    
    class Meta:
        model = Synthesis
        fields = ('id', 'text', 'voice', 'created_at')
        read_only_fields = ('id', 'created_at')


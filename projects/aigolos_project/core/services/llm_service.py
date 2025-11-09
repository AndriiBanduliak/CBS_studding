"""
LLM Service - Language Model interactions using Ollama.
"""

import logging
from typing import Optional
import httpx
from django.conf import settings
from core.exceptions import LLMServiceError

logger = logging.getLogger('core')


class LLMService:
    """Service for LLM interactions using Ollama."""
    
    def __init__(self):
        """Initialize LLM service."""
        self.base_url = settings.OLLAMA_BASE_URL
        self.model_name = settings.LLM_MODEL_NAME
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.temperature = settings.LLM_TEMPERATURE
        self._client = None
    
    @property
    def client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                timeout=60.0
            )
        return self._client
    
    def _build_conversation_context(self, conversation_id: Optional[str]) -> str:
        """Build conversation context from history."""
        if not conversation_id:
            return ""
        
        try:
            from llm.models import Conversation, Message
            conversation = Conversation.objects.filter(id=conversation_id).first()
            if not conversation:
                return ""
            
            # Get recent messages (last 10 for context)
            messages = Message.objects.filter(
                conversation=conversation
            ).order_by('-created_at')[:10]
            
            # Build context from messages (reverse to get chronological order)
            context_parts = []
            for msg in reversed(messages):
                role_prefix = "User" if msg.role == 'user' else "Assistant"
                context_parts.append(f"{role_prefix}: {msg.content}")
            
            if context_parts:
                return "\n".join(context_parts) + "\n\n"
            return ""
        except Exception as e:
            logger.warning(f"Failed to build conversation context: {e}")
            return ""
    
    def generate(
        self,
        message: str,
        conversation_id: Optional[str] = None
    ) -> str:
        """
        Generate response from LLM.
        
        Args:
            message: User message
            conversation_id: Optional conversation ID for context
            
        Returns:
            AI response text
            
        Raises:
            LLMServiceError: If generation fails
        """
        try:
            # Build conversation context if conversation_id is provided
            context = self._build_conversation_context(conversation_id)
            
            # Prepare prompt with context
            if context:
                full_prompt = f"{context}User: {message}\nAssistant:"
            else:
                full_prompt = message
            
            # Prepare request
            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            }
            
            # Make request to Ollama
            response = self.client.post(
                "/api/generate",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            ai_response = result.get("response", "")
            
            logger.info(f"LLM response generated (length: {len(ai_response)}, context_used={bool(context)})")
            return ai_response.strip()
            
        except httpx.ConnectError as e:
            logger.error(f"Ollama connection failed: {e}", exc_info=True)
            raise LLMServiceError(
                f"Не удалось подключиться к Ollama. Убедитесь, что Ollama запущен:\n"
                f"1. Установите Ollama: https://ollama.ai\n"
                f"2. Запустите: ollama serve\n"
                f"3. Проверьте URL: {self.base_url}\n"
                f"Ошибка: {str(e)}"
            )
        except httpx.HTTPError as e:
            logger.error(f"LLM request failed: {e}", exc_info=True)
            raise LLMServiceError(f"Ошибка запроса к Ollama: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in LLM service: {e}", exc_info=True)
            raise LLMServiceError(f"Ошибка LLM сервиса: {e}")
    
    def close(self):
        """Close HTTP client."""
        if self._client:
            self._client.close()
            self._client = None


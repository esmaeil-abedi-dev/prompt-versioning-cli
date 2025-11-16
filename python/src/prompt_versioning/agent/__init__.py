"""
LLM-powered conversational agent for natural language prompt versioning.

This module provides:
- PromptVCAgent: Main agent class for conversational interaction
- AgentResponse: Response object from agent interactions
- ConversationMessage: Message history tracking
- LLM backends: OpenAI, Anthropic, Ollama

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from .agent import PromptVCAgent, get_default_backend
from .backends.anthropic_backend import AnthropicBackend
from .backends.base import LLMBackend
from .backends.ollama_backend import OllamaBackend
from .backends.openai_backend import OpenAIBackend
from .models import AgentResponse, ConversationMessage

__all__ = [
    "PromptVCAgent",
    "get_default_backend",
    "AgentResponse",
    "ConversationMessage",
    "LLMBackend",
    "OpenAIBackend",
    "AnthropicBackend",
    "OllamaBackend",
]

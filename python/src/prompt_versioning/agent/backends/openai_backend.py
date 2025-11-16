"""
OpenAI API backend for LLM agent.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import os
from typing import Optional

from .base import LLMBackend


class OpenAIBackend(LLMBackend):
    """OpenAI API backend (GPT-4, GPT-3.5, etc.)."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize OpenAI backend.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model name (gpt-4, gpt-3.5-turbo, etc.)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self._client = None

    def _get_client(self):
        """Lazy-load OpenAI client."""
        if self._client is None:
            try:
                import openai

                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError as err:
                raise ImportError(
                    "OpenAI package not installed. Install with: pip install openai"
                ) from err
        return self._client

    def generate(
        self, messages: list[dict[str, str]], temperature: float = 0.7, max_tokens: int = 500
    ) -> str:
        """Generate completion using OpenAI API."""
        client = self._get_client()

        response = client.chat.completions.create(
            model=self.model, messages=messages, temperature=temperature, max_tokens=max_tokens
        )

        return response.choices[0].message.content

    def is_available(self) -> bool:
        """Check if OpenAI backend is available."""
        if not self.api_key:
            return False
        try:
            import openai  # noqa: F401

            return True
        except ImportError:
            return False

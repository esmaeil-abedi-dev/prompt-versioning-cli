"""
Anthropic API backend for LLM agent.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import os
from typing import Optional

from .base import LLMBackend


class AnthropicBackend(LLMBackend):
    """Anthropic API backend (Claude)."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize Anthropic backend.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model name
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self._client = None

    def _get_client(self):
        """Lazy-load Anthropic client."""
        if self._client is None:
            try:
                import anthropic

                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError as err:
                raise ImportError(
                    "Anthropic package not installed. Install with: pip install anthropic"
                ) from err
        return self._client

    def generate(
        self, messages: list[dict[str, str]], temperature: float = 0.7, max_tokens: int = 500
    ) -> str:
        """Generate completion using Anthropic API."""
        client = self._get_client()

        # Anthropic uses system parameter separately
        system_msg = None
        chat_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                chat_messages.append(msg)

        response = client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_msg,
            messages=chat_messages,
        )

        return response.content[0].text

    def is_available(self) -> bool:
        """Check if Anthropic backend is available."""
        if not self.api_key:
            return False
        try:
            import anthropic  # noqa: F401

            return True
        except ImportError:
            return False

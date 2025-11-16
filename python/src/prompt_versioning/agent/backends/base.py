"""
Abstract base class for LLM backends.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from abc import ABC, abstractmethod


class LLMBackend(ABC):
    """Abstract base class for LLM backends."""

    @abstractmethod
    def generate(
        self, messages: list[dict[str, str]], temperature: float = 0.7, max_tokens: int = 500
    ) -> str:
        """
        Generate a completion from the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is properly configured and available."""
        pass

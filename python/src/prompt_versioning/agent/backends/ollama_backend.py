"""
Ollama API backend for LLM agent (local inference).

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from typing import Any

from .base import LLMBackend


class OllamaBackend(LLMBackend):
    """Local Ollama backend for privacy-focused deployments."""

    def __init__(self, model: str = "llama3.2", host: str = "http://localhost:11434"):
        """
        Initialize Ollama backend.

        Args:
            model: Model name (llama3.2, mistral, codellama, etc.)
            host: Ollama server URL
        """
        self.model = model
        self.host = host

    def generate(
        self, messages: list[dict[str, str]], temperature: float = 0.7, max_tokens: int = 500
    ) -> str:
        """Generate completion using Ollama."""
        try:
            import requests
        except ImportError as err:
            raise ImportError(
                "Requests package not installed. Install with: pip install requests"
            ) from err

        # Convert messages to Ollama format
        prompt = self._format_messages(messages)

        response = requests.post(
            f"{self.host}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature, "num_predict": max_tokens},
            },
        )

        response.raise_for_status()
        result: dict[str, Any] = response.json()
        return str(result["response"])

    def _format_messages(self, messages: list[dict[str, str]]) -> str:
        """Convert chat messages to a single prompt string."""
        parts = []
        for msg in messages:
            role = msg["role"].capitalize()
            content = msg["content"]
            parts.append(f"{role}: {content}")
        return "\n\n".join(parts) + "\n\nAssistant:"

    def is_available(self) -> bool:
        """Check if Ollama server is running."""
        try:
            import requests

            response = requests.get(f"{self.host}/api/tags", timeout=2)
            is_available: bool = response.status_code == 200
            return is_available
        except Exception:
            return False

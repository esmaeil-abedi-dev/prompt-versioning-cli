"""
Tests for Ollama backend.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import pytest

from prompt_versioning.agent.backends import OllamaBackend


class TestOllamaBackend:
    """Test Ollama backend implementation."""

    def test_ollama_backend_init(self):
        """Test Ollama backend initialization."""
        backend = OllamaBackend(model="llama3.2", host="http://localhost:11434")
        assert backend.model == "llama3.2"
        assert backend.host == "http://localhost:11434"

    def test_ollama_backend_default_host(self):
        """Test Ollama backend with default host."""
        backend = OllamaBackend(model="llama3.2")
        assert backend.host == "http://localhost:11434"

    def test_ollama_backend_default_model(self):
        """Test Ollama backend with default model."""
        backend = OllamaBackend()
        assert backend.model == "llama3.2"

    def test_ollama_is_available(self):
        """Test Ollama availability check."""
        backend = OllamaBackend()
        # Should check if Ollama is running locally
        assert isinstance(backend.is_available(), bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

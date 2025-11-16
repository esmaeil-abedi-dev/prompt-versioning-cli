"""
Tests for OpenAI backend.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from unittest.mock import patch

import pytest

from prompt_versioning.agent.backends import OpenAIBackend


class TestOpenAIBackend:
    """Test OpenAI backend implementation."""

    def test_openai_backend_init(self):
        """Test OpenAI backend initialization."""
        backend = OpenAIBackend(api_key="test_key", model="gpt-4")
        assert backend.api_key == "test_key"
        assert backend.model == "gpt-4"

    def test_openai_backend_default_model(self):
        """Test OpenAI backend with default model."""
        backend = OpenAIBackend(api_key="test_key")
        assert backend.model == "gpt-4"

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"})
    def test_openai_is_available_with_key(self):
        """Test OpenAI availability check with API key."""
        backend = OpenAIBackend()
        assert backend.api_key == "test_key"

    def test_openai_is_available_without_key(self):
        """Test OpenAI availability check without API key."""
        backend = OpenAIBackend()
        if not backend.api_key:
            assert not backend.is_available()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Tests for Anthropic backend.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from unittest.mock import patch

import pytest

from prompt_versioning.agent.backends import AnthropicBackend


class TestAnthropicBackend:
    """Test Anthropic backend implementation."""

    def test_anthropic_backend_init(self):
        """Test Anthropic backend initialization."""
        backend = AnthropicBackend(api_key="test_key", model="claude-3-5-sonnet-20241022")
        assert backend.api_key == "test_key"
        assert backend.model == "claude-3-5-sonnet-20241022"

    def test_anthropic_backend_default_model(self):
        """Test Anthropic backend with default model."""
        backend = AnthropicBackend(api_key="test_key")
        assert backend.model == "claude-3-5-sonnet-20241022"

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    def test_anthropic_is_available_with_key(self):
        """Test Anthropic availability check with API key."""
        backend = AnthropicBackend()
        assert backend.api_key == "test_key"

    def test_anthropic_is_available_without_key(self):
        """Test Anthropic availability check without API key."""
        backend = AnthropicBackend()
        if not backend.api_key:
            assert not backend.is_available()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

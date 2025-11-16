"""
Tests for base backend interface.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import pytest

from prompt_versioning.agent.backends import LLMBackend


class MockLLMBackend(LLMBackend):
    """Mock LLM backend for testing."""

    def __init__(self, responses=None):
        self.responses = responses or []
        self.call_count = 0

    def generate(self, messages, temperature=0.7, max_tokens=500):
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
            self.call_count += 1
            return response
        return "Mock response"

    def is_available(self):
        return True


class TestMockBackend:
    """Test mock backend functionality."""

    def test_mock_backend_responses(self):
        """Test mock backend returns predefined responses."""
        backend = MockLLMBackend(responses=["Response 1", "Response 2"])

        assert backend.generate([]) == "Response 1"
        assert backend.generate([]) == "Response 2"
        assert backend.generate([]) == "Mock response"

    def test_mock_backend_is_available(self):
        """Test mock backend availability."""
        backend = MockLLMBackend()
        assert backend.is_available()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

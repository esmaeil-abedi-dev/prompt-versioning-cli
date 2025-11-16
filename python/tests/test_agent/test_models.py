"""
Tests for agent models (AgentResponse, ConversationMessage, etc.).

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from datetime import datetime

import pytest

from prompt_versioning.agent.models import AgentResponse, ConversationMessage


class TestAgentResponse:
    """Test AgentResponse model."""

    def test_agent_response_creation(self):
        """Test creating an AgentResponse."""
        response = AgentResponse(
            message="Test message", command="promptvc init", needs_confirmation=False
        )

        assert response.message == "Test message"
        assert response.command == "promptvc init"
        assert not response.needs_confirmation
        assert response.error is None

    def test_agent_response_with_error(self):
        """Test AgentResponse with error."""
        response = AgentResponse(message="Error occurred", error="API Error")

        assert response.error == "API Error"
        assert response.command is None


class TestConversationMessage:
    """Test ConversationMessage model."""

    def test_conversation_message_creation(self):
        """Test creating a ConversationMessage."""
        message = ConversationMessage(role="user", content="Hello")

        assert message.role == "user"
        assert message.content == "Hello"
        assert isinstance(message.timestamp, datetime)

    def test_conversation_message_to_dict(self):
        """Test converting message to dict."""
        from dataclasses import asdict

        message = ConversationMessage(role="assistant", content="Hi there")

        data = asdict(message)

        assert data["role"] == "assistant"
        assert data["content"] == "Hi there"
        assert "timestamp" in data

    def test_conversation_message_from_dict(self):
        """Test creating message from dict."""
        timestamp = datetime.now()
        data = {"role": "user", "content": "Test", "timestamp": timestamp, "metadata": {}}

        message = ConversationMessage(**data)

        assert message.role == "user"
        assert message.content == "Test"
        assert message.timestamp == timestamp


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

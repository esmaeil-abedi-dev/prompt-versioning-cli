"""
Tests for conversation management.

Tests cover:
- Conversation history
- Message saving/loading
- Multi-turn interactions

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import json
from datetime import datetime

import pytest

from prompt_versioning.agent import PromptVCAgent
from prompt_versioning.agent.models import ConversationMessage

from .test_backends.test_base import MockLLMBackend


@pytest.fixture
def temp_repo(tmp_path):
    """Create a temporary repository for testing."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    return repo_path


@pytest.fixture
def mock_backend():
    """Create a mock LLM backend."""
    return MockLLMBackend(
        responses=[
            "I'll initialize the repository.\n```command\npromptvc init\n```",
            "Here are the commits.\n```command\npromptvc log -n 5\n```",
        ]
    )


@pytest.fixture
def agent(temp_repo, mock_backend):
    """Create an agent with mock backend."""
    return PromptVCAgent(backend=mock_backend, repo_path=str(temp_repo))


class TestConversationHistory:
    """Test conversation history management."""

    def test_agent_init_empty_history(self, temp_repo, mock_backend):
        """Test agent initialization with empty history."""
        agent = PromptVCAgent(backend=mock_backend, repo_path=str(temp_repo))
        assert len(agent.conversation_history) == 0

    def test_agent_init_with_history(self, temp_repo, mock_backend):
        """Test agent initialization with existing conversation."""
        history = [
            ConversationMessage(role="user", content="Hello"),
            ConversationMessage(role="assistant", content="Hi there!"),
        ]
        agent = PromptVCAgent(
            backend=mock_backend, repo_path=str(temp_repo), conversation_history=history
        )
        assert len(agent.conversation_history) == 2

    def test_process_message_updates_history(self, agent):
        """Test that processing messages updates history."""
        agent.process_message("initialize the project")
        assert len(agent.conversation_history) == 2  # user + assistant

        agent.process_message("show status")
        assert len(agent.conversation_history) == 4  # 2 more messages

    def test_conversation_history_truncation(self, agent):
        """Test that conversation history is truncated."""
        # Add many messages
        for i in range(20):
            agent.conversation_history.append(
                ConversationMessage(role="user", content=f"Message {i}")
            )

        agent.process_message("test")
        assert len(agent.conversation_history) == 22  # 20 + 2 new


class TestConversationPersistence:
    """Test conversation saving and loading."""

    def test_save_conversation(self, agent, temp_repo):
        """Test saving conversation to file."""
        agent.process_message("hello")
        agent.process_message("show status")

        filepath = temp_repo / "conversation.json"
        agent.save_conversation(filepath)

        assert filepath.exists()

        with open(filepath) as f:
            data = json.load(f)

        assert len(data) == 4  # 2 user + 2 assistant messages
        assert data[0]["role"] == "user"
        assert data[0]["content"] == "hello"

    def test_load_conversation(self, temp_repo, mock_backend):
        """Test loading conversation from file."""
        # Create conversation file
        conversation_data = [
            {
                "role": "user",
                "content": "hello",
                "timestamp": datetime.now().isoformat(),
                "metadata": {},
            },
            {
                "role": "assistant",
                "content": "Hi there!",
                "timestamp": datetime.now().isoformat(),
                "metadata": {},
            },
        ]

        filepath = temp_repo / "conversation.json"
        with open(filepath, "w") as f:
            json.dump(conversation_data, f)

        # Load conversation
        loaded_agent = PromptVCAgent.load_conversation(
            filepath, backend=mock_backend, repo_path=str(temp_repo)
        )

        assert len(loaded_agent.conversation_history) == 2
        assert loaded_agent.conversation_history[0].role == "user"
        assert loaded_agent.conversation_history[0].content == "hello"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

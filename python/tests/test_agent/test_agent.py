"""
Unit tests for agent core functionality.

Tests cover:
- Agent initialization
- Command parsing and extraction
- Message processing
- Error handling
- Edge cases

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import json
from datetime import datetime
from unittest.mock import Mock

import pytest

from prompt_versioning.agent import PromptVCAgent
from prompt_versioning.agent.models import AgentResponse, ConversationMessage

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
            "I'll show you the diff.\n```command\npromptvc diff abc123 HEAD\n```",
        ]
    )


@pytest.fixture
def agent(temp_repo, mock_backend):
    """Create an agent with mock backend."""
    return PromptVCAgent(backend=mock_backend, repo_path=str(temp_repo))


class TestAgentInitialization:
    """Test agent initialization."""

    def test_agent_init_with_backend(self, temp_repo, mock_backend):
        """Test agent initialization with explicit backend."""
        agent = PromptVCAgent(backend=mock_backend, repo_path=str(temp_repo))
        assert agent.backend == mock_backend
        assert agent.repo_path == temp_repo
        assert len(agent.conversation_history) == 0

    def test_agent_auto_detect_backend_failure(self, temp_repo, monkeypatch):
        """Test agent backend auto-detection failure."""

        # Mock all backends to be unavailable
        def mock_unavailable(*args, **kwargs):
            return False

        monkeypatch.setattr(
            "prompt_versioning.agent.backends.openai_backend.OpenAIBackend.is_available",
            mock_unavailable,
        )
        monkeypatch.setattr(
            "prompt_versioning.agent.backends.anthropic_backend.AnthropicBackend.is_available",
            mock_unavailable,
        )
        monkeypatch.setattr(
            "prompt_versioning.agent.backends.ollama_backend.OllamaBackend.is_available",
            mock_unavailable,
        )

        with pytest.raises(RuntimeError, match="No LLM backend available"):
            PromptVCAgent(repo_path=str(temp_repo))


class TestCommandExtraction:
    """Test command parsing and extraction."""

    def test_extract_command_basic(self, agent):
        """Test extracting basic command."""
        response = "I'll initialize the repo.\n```command\npromptvc init\n```"
        cmd, args = agent._extract_command(response)

        assert cmd == "promptvc init"
        assert args["action"] == "init"

    def test_extract_command_with_args(self, agent):
        """Test extracting command with arguments."""
        response = "```command\npromptvc commit -m 'message' -f file.yaml\n```"
        cmd, args = agent._extract_command(response)

        assert cmd == "promptvc commit -m 'message' -f file.yaml"
        assert args["action"] == "commit"
        assert args["m"] == "message"
        assert args["f"] == "file.yaml"

    def test_extract_command_bash_block(self, agent):
        """Test extracting command from bash block."""
        response = "```bash\npromptvc log -n 5\n```"
        cmd, args = agent._extract_command(response)

        assert cmd == "promptvc log -n 5"
        assert args["action"] == "log"
        assert args["n"] == "5"

    def test_extract_command_no_command(self, agent):
        """Test response without command."""
        response = "Here's some information about the repository."
        result = agent._extract_command(response)

        assert result is None

    def test_parse_command_flags(self, agent):
        """Test parsing command with flags."""
        cmd = "promptvc log --oneline --max-count 10"
        args = agent._parse_command(cmd)

        assert args["action"] == "log"
        assert args["oneline"]
        assert args["max-count"] == "10"


class TestAgentInteraction:
    """Test agent interaction and response processing."""

    def test_process_message_basic(self, agent):
        """Test processing a basic message."""
        response = agent.process_message("initialize the project")

        assert isinstance(response, AgentResponse)
        assert response.message
        assert response.command
        assert "promptvc init" in response.command

    def test_process_message_with_history(self, agent):
        """Test multi-turn conversation with history."""
        # First message
        agent.process_message("initialize the project")
        assert len(agent.conversation_history) == 2  # user + assistant

        # Second message (should have context)
        response2 = agent.process_message("now show me the status")
        assert len(agent.conversation_history) == 4  # 2 more messages
        assert response2.command

    def test_process_message_needs_confirmation(self, agent):
        """Test messages that need confirmation."""
        agent.backend.responses = [
            "I'll checkout that version.\n```command\npromptvc checkout abc123\n```"
        ]

        response = agent.process_message("switch to version abc123")
        assert response.needs_confirmation

    def test_process_message_error_handling(self, agent):
        """Test error handling in message processing."""
        # Make backend raise an error
        agent.backend.generate = Mock(side_effect=Exception("API Error"))

        response = agent.process_message("show commits")
        assert response.error is not None
        assert "API Error" in response.error


class TestConversationManagement:
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

    def test_load_conversation(self, agent, temp_repo, mock_backend):
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


class TestSystemPrompt:
    """Test system prompt generation."""

    def test_system_prompt_includes_context(self, agent):
        """Test that system prompt includes repo context."""
        system_prompt = agent._build_system_prompt()

        assert str(agent.repo_path.resolve()) in system_prompt
        assert "promptvc" in system_prompt.lower()

    def test_repo_status_not_initialized(self, agent):
        """Test repo status when not initialized."""
        status = agent._get_repo_status()
        assert "Not initialized" in status

    def test_repo_status_initialized_no_commits(self, agent, temp_repo):
        """Test repo status when initialized but no commits."""
        from prompt_versioning.core import PromptRepository

        # Initialize repo
        PromptRepository.init(temp_repo)
        agent.repo = PromptRepository(temp_repo)
        agent.repo_exists = True

        status = agent._get_repo_status()
        assert "Initialized" in status


class TestIntegration:
    """Integration tests with real repository operations."""

    def test_agent_with_real_repo(self, temp_repo, mock_backend):
        """Test agent with actual repository operations."""
        from prompt_versioning.core import PromptRepository

        # Initialize real repo
        PromptRepository.init(temp_repo)

        # Create agent
        agent = PromptVCAgent(backend=mock_backend, repo_path=str(temp_repo))

        # Test status query
        mock_backend.responses = [
            "The repository is initialized.\n```command\npromptvc status\n```"
        ]

        response = agent.process_message("what's the status?")
        assert response.command
        assert "status" in response.command


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_message(self, agent):
        """Test processing empty message."""
        response = agent.process_message("")
        assert isinstance(response, AgentResponse)

    def test_very_long_message(self, agent):
        """Test processing very long message."""
        long_message = "show commits " * 1000
        response = agent.process_message(long_message)
        assert isinstance(response, AgentResponse)

    def test_special_characters_in_message(self, agent):
        """Test message with special characters."""
        response = agent.process_message("commit with message 'test \"quoted\" value'")
        assert isinstance(response, AgentResponse)

    def test_multiple_commands_in_response(self, agent):
        """Test response with multiple command blocks."""
        agent.backend.responses = [
            "First, init:\n```command\npromptvc init\n```\nThen commit:\n```command\npromptvc commit\n```"
        ]

        response = agent.process_message("set up and commit")
        # Should extract first command
        assert response.command
        assert "init" in response.command


class TestMocking:
    """Test mock backend functionality."""

    def test_mock_backend_responses(self):
        """Test mock backend returns predefined responses."""
        backend = MockLLMBackend(responses=["Response 1", "Response 2"])

        assert backend.generate([]) == "Response 1"
        assert backend.generate([]) == "Response 2"
        assert backend.generate([]) == "Mock response"  # Default after exhausting

    def test_mock_backend_is_available(self):
        """Test mock backend availability."""
        backend = MockLLMBackend()
        assert backend.is_available()


# Performance tests
class TestPerformance:
    """Test performance characteristics."""

    def test_conversation_history_truncation(self, agent):
        """Test that conversation history is truncated."""
        # Add many messages
        for i in range(20):
            agent.conversation_history.append(
                ConversationMessage(role="user", content=f"Message {i}")
            )

        # Process should only use last 10
        agent.process_message("test")
        # Implementation limits to 10 messages in _build_messages
        assert len(agent.conversation_history) == 22  # 20 + 2 new


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

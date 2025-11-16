"""
Tests for core data models.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import pytest

from prompt_versioning.core.models import ExperimentTag, Prompt, PromptCommit, PromptVersion


class TestPromptModel:
    """Test Prompt data model."""

    def test_prompt_creation(self):
        """Test creating a Prompt."""
        prompt = Prompt(system="You are helpful", temperature=0.7, max_tokens=500)

        assert prompt.system == "You are helpful"
        assert prompt.temperature == 0.7
        assert prompt.max_tokens == 500

    def test_prompt_to_dict(self):
        """Test converting Prompt to dict."""
        prompt = Prompt(system="Test")
        data = prompt.model_dump()

        assert data["system"] == "Test"
        assert isinstance(data, dict)


class TestPromptCommit:
    """Test PromptCommit data model."""

    def test_commit_creation(self):
        """Test creating a PromptCommit."""
        commit = PromptCommit(
            hash="abc123", message="Initial commit", author="test_user", prompt_hash="def456"
        )

        assert commit.hash == "abc123"
        assert commit.message == "Initial commit"
        assert commit.author == "test_user"
        assert commit.prompt_hash == "def456"


class TestExperimentTag:
    """Test ExperimentTag data model."""

    def test_tag_creation(self):
        """Test creating an ExperimentTag."""
        tag = ExperimentTag(name="v1.0", commit_hash="abc123", metadata={"version": "1.0"})

        assert tag.name == "v1.0"
        assert tag.commit_hash == "abc123"
        assert tag.metadata["version"] == "1.0"


class TestPromptVersion:
    """Test PromptVersion data model."""

    def test_version_creation(self):
        """Test creating a PromptVersion."""
        commit = PromptCommit(hash="abc123", message="Test", author="user", prompt_hash="def456")
        prompt = Prompt(system="Test")

        version = PromptVersion(commit=commit, prompt=prompt)

        assert version.commit == commit
        assert version.prompt == prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

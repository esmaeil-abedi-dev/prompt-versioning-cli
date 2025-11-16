"""
Test suite for core version control functionality.

Tests the main PromptRepository class and its operations.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from prompt_versioning.core import PromptRepository


class TestPromptRepository:
    """Test cases for PromptRepository operations."""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir)

    def test_init_repository(self, temp_repo):
        """Test repository initialization."""
        repo = PromptRepository.init(temp_repo)

        assert repo.exists()
        assert (temp_repo / ".prompt-vc").exists()
        assert (temp_repo / ".prompt-vc" / "HEAD").exists()
        assert (temp_repo / ".prompt-vc" / "config.json").exists()

    def test_init_existing_repository_fails(self, temp_repo):
        """Test that initializing an existing repository raises error."""
        PromptRepository.init(temp_repo)

        with pytest.raises(FileExistsError):
            PromptRepository.init(temp_repo)

    def test_commit_prompt(self, temp_repo):
        """Test creating a commit."""
        repo = PromptRepository.init(temp_repo)

        prompt_data = {
            "system": "You are a helpful assistant.",
            "temperature": 0.7,
            "max_tokens": 500,
        }

        commit = repo.commit("Initial prompt", prompt_data, author="test_user")

        assert commit.hash
        assert commit.message == "Initial prompt"
        assert commit.author == "test_user"
        assert commit.parent_hash is None  # First commit has no parent

    def test_commit_sequence(self, temp_repo):
        """Test creating multiple commits in sequence."""
        repo = PromptRepository.init(temp_repo)

        # First commit
        commit1 = repo.commit("First", {"system": "Version 1"})

        # Second commit
        commit2 = repo.commit("Second", {"system": "Version 2"})

        assert commit2.parent_hash == commit1.hash
        assert commit1.hash != commit2.hash

    def test_log(self, temp_repo):
        """Test viewing commit history."""
        repo = PromptRepository.init(temp_repo)

        # Create multiple commits
        repo.commit("First", {"system": "V1"})
        repo.commit("Second", {"system": "V2"})
        repo.commit("Third", {"system": "V3"})

        # Get log
        versions = repo.log()

        assert len(versions) == 3
        assert versions[0].commit.message == "Third"  # Newest first
        assert versions[1].commit.message == "Second"
        assert versions[2].commit.message == "First"

    def test_log_with_max_count(self, temp_repo):
        """Test limiting log output."""
        repo = PromptRepository.init(temp_repo)

        for i in range(5):
            repo.commit(f"Commit {i}", {"system": f"V{i}"})

        versions = repo.log(max_count=3)

        assert len(versions) == 3

    def test_diff(self, temp_repo):
        """Test diffing two commits."""
        repo = PromptRepository.init(temp_repo)

        commit1 = repo.commit(
            "First",
            {
                "system": "You are helpful.",
                "temperature": 0.7,
            },
        )

        commit2 = repo.commit(
            "Second",
            {
                "system": "You are very helpful.",
                "temperature": 0.9,
            },
        )

        diff = repo.diff(commit1.hash, commit2.hash)

        assert diff.has_changes()
        assert len(diff.changes) == 2  # system and temperature changed

    def test_diff_with_short_hash(self, temp_repo):
        """Test diff with abbreviated commit hashes."""
        repo = PromptRepository.init(temp_repo)

        commit1 = repo.commit("First", {"system": "V1"})
        commit2 = repo.commit("Second", {"system": "V2"})

        # Use short hashes (first 7 chars)
        diff = repo.diff(commit1.hash[:7], commit2.hash[:7])

        assert diff.has_changes()

    def test_checkout(self, temp_repo):
        """Test checking out a previous commit."""
        repo = PromptRepository.init(temp_repo)

        commit1 = repo.commit("First", {"system": "V1"})
        repo.commit("Second", {"system": "V2"})

        # Checkout first commit
        version = repo.checkout(commit1.hash)

        assert version.commit.hash == commit1.hash
        assert repo.get_current_version().commit.hash == commit1.hash

    def test_tag_creation(self, temp_repo):
        """Test creating experiment tags."""
        repo = PromptRepository.init(temp_repo)

        commit = repo.commit("Test", {"system": "V1"})

        # Create tag with metadata
        tag = repo.tag("experiment-baseline", metadata={"accuracy": 0.85, "model": "gpt-4"})

        assert tag.name == "experiment-baseline"
        assert tag.commit_hash == commit.hash
        assert tag.metadata["accuracy"] == 0.85

    def test_tag_retrieval(self, temp_repo):
        """Test retrieving tags."""
        repo = PromptRepository.init(temp_repo)

        repo.commit("Test", {"system": "V1"})
        repo.tag("test-tag", metadata={"test": True})

        # Get tag
        tag = repo.get_tag("test-tag")

        assert tag is not None
        assert tag.name == "test-tag"
        assert tag.metadata["test"] is True

    def test_list_tags(self, temp_repo):
        """Test listing all tags."""
        repo = PromptRepository.init(temp_repo)

        repo.commit("Test", {"system": "V1"})
        repo.tag("tag1")
        repo.tag("tag2")
        repo.tag("tag3")

        tags = repo.list_tags()

        assert len(tags) == 3
        tag_names = [t.name for t in tags]
        assert "tag1" in tag_names
        assert "tag2" in tag_names
        assert "tag3" in tag_names

    def test_head_reference(self, temp_repo):
        """Test HEAD reference resolution."""
        repo = PromptRepository.init(temp_repo)

        repo.commit("First", {"system": "V1"})
        commit2 = repo.commit("Second", {"system": "V2"})

        # HEAD should point to latest commit
        current = repo.get_current_version()
        assert current.commit.hash == commit2.hash

    def test_head_tilde_reference(self, temp_repo):
        """Test HEAD~N reference resolution."""
        repo = PromptRepository.init(temp_repo)

        repo.commit("First", {"system": "V1"})
        repo.commit("Second", {"system": "V2"})
        repo.commit("Third", {"system": "V3"})

        # HEAD~1 should be second commit
        diff = repo.diff("HEAD~1", "HEAD")
        assert diff.has_changes()

        # HEAD~2 should be first commit
        diff = repo.diff("HEAD~2", "HEAD")
        assert diff.has_changes()

    def test_audit_log(self, temp_repo):
        """Test audit log generation."""
        repo = PromptRepository.init(temp_repo)

        repo.commit("First", {"system": "V1"})
        repo.commit("Second", {"system": "V2"})
        repo.tag("test-tag")

        # Get audit log as dict
        audit_data = repo.audit_log(format="dict")

        assert len(audit_data) >= 4  # init + 2 commits + tag

        # Check action types
        actions = [entry["action"] for entry in audit_data]
        assert "init" in actions
        assert "commit" in actions
        assert "tag" in actions

    def test_audit_log_csv_format(self, temp_repo):
        """Test CSV format audit log."""
        repo = PromptRepository.init(temp_repo)

        repo.commit("Test", {"system": "V1"})

        csv_output = repo.audit_log(format="csv")

        assert "timestamp,action,commit_hash" in csv_output
        assert "commit" in csv_output

    def test_empty_repository_log(self, temp_repo):
        """Test log on empty repository."""
        repo = PromptRepository.init(temp_repo)

        versions = repo.log()

        assert len(versions) == 0

    def test_commit_without_init_fails(self, temp_repo):
        """Test that committing without init raises error."""
        repo = PromptRepository(temp_repo)

        with pytest.raises(ValueError, match="not initialized"):
            repo.commit("Test", {"system": "V1"})

    def test_prompt_hash_consistency(self, temp_repo):
        """Test that identical prompts produce same hash."""
        repo = PromptRepository.init(temp_repo)

        prompt_data = {"system": "Test", "temperature": 0.7}

        commit1 = repo.commit("First", prompt_data)
        commit2 = repo.commit("Second", prompt_data)  # Same data

        # Both should reference same prompt hash (content-addressable storage)
        assert commit1.prompt_hash == commit2.prompt_hash

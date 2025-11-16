"""
Tests for CLI commands.

Tests organized by command:
- init, commit, log, diff, checkout
- tag, tags, status, audit
- agent, mcp, mcp-setup

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import shutil
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from prompt_versioning.cli import cli


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp = Path(tempfile.mkdtemp())
    yield temp
    shutil.rmtree(temp)


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


class TestInitCommand:
    """Test the init command."""

    def test_init_creates_repository(self, runner, temp_dir):
        """Test that init command creates a repository."""
        result = runner.invoke(cli, ["init", "--path", str(temp_dir)])

        assert result.exit_code == 0
        assert (temp_dir / ".prompt-vc").exists()
        assert "Initialized" in result.output

    def test_init_existing_repository_fails(self, runner, temp_dir):
        """Test that initializing an existing repository fails."""
        # First init
        runner.invoke(cli, ["init", "--path", str(temp_dir)])

        # Second init should fail
        result = runner.invoke(cli, ["init", "--path", str(temp_dir)])

        assert result.exit_code != 0
        assert "already exists" in result.output


class TestCommitCommand:
    """Test the commit command."""

    def test_commit_requires_message(self, runner, temp_dir):
        """Test that commit requires a message."""
        runner.invoke(cli, ["init", "--path", str(temp_dir)])

        result = runner.invoke(cli, ["commit", "--path", str(temp_dir)])

        assert result.exit_code != 0


class TestLogCommand:
    """Test the log command."""

    def test_log_empty_repository(self, runner, temp_dir):
        """Test log on empty repository."""
        runner.invoke(cli, ["init", "--path", str(temp_dir)])

        result = runner.invoke(cli, ["log", "--path", str(temp_dir)])

        assert result.exit_code == 0


class TestStatusCommand:
    """Test the status command."""

    def test_status_initialized_repo(self, runner, temp_dir):
        """Test status on initialized repository."""
        runner.invoke(cli, ["init", "--path", str(temp_dir)])

        result = runner.invoke(cli, ["status", "--path", str(temp_dir)])

        assert result.exit_code == 0
        assert "no commits" in result.output.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

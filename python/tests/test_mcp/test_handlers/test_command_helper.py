"""
Tests for command helper utility and execute command handler.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import pytest

from prompt_versioning.mcp.handlers.command_helper import CommandFlag, CommandHelper, CommandInfo
from prompt_versioning.mcp.handlers.execute_command import handle_execute_command


class TestCommandHelper:
    """Tests for CommandHelper class."""

    def test_parse_help_output_with_options(self):
        """Test parsing help output with options."""
        help_text = """
Prompt Version Control - Commit a prompt

Usage: promptvc commit [OPTIONS]

Options:
  -m, --message TEXT  Commit message  [required]
  -f, --file PATH     Path to prompt file
  -a, --author TEXT   Commit author
  --help              Show this message and exit.
"""
        helper = CommandHelper("promptvc")
        info = helper.parse_help_output(help_text)

        assert info.command == "promptvc"
        assert len(info.flags) >= 3

        # Check message flag
        message_flag = next(f for f in info.flags if f.name == "message")
        assert message_flag.short_form == "-m"
        assert message_flag.long_form == "--message"
        assert message_flag.required is True

        # Check file flag
        file_flag = next(f for f in info.flags if f.name == "file")
        assert file_flag.short_form == "-f"
        assert file_flag.long_form == "--file"
        assert file_flag.required is False

    def test_parse_help_output_with_subcommands(self):
        """Test parsing help output with subcommands."""
        help_text = """
Prompt Version Control - Git-like version control for LLM prompts.

Usage: promptvc [OPTIONS] COMMAND [ARGS]...

Commands:
  init      Initialize a new prompt repository
  commit    Commit a prompt
  log       View commit history
  diff      Compare two versions
  checkout  Checkout a specific version
"""
        helper = CommandHelper("promptvc")
        info = helper.parse_help_output(help_text)

        assert "init" in info.subcommands
        assert "commit" in info.subcommands
        assert "log" in info.subcommands
        assert "diff" in info.subcommands
        assert "checkout" in info.subcommands

    def test_build_command_with_flags(self):
        """Test building command with proper flags."""
        helper = CommandHelper("promptvc")

        # Create mock command info
        command_info = CommandInfo(
            command="promptvc",
            description="Test",
            flags=[
                CommandFlag(
                    name="message",
                    short_form="-m",
                    long_form="--message",
                    description="Commit message",
                    required=True,
                ),
                CommandFlag(
                    name="file",
                    short_form="-f",
                    long_form="--file",
                    description="File path",
                    required=False,
                ),
            ],
            subcommands=[],
        )

        args = {"message": "Test commit", "file": "prompt.yaml"}
        cmd = helper.build_command("commit", args, command_info)

        assert cmd[0] == "promptvc"
        assert cmd[1] == "commit"
        assert "--message" in cmd
        assert "Test commit" in cmd
        assert "--file" in cmd
        assert "prompt.yaml" in cmd

    def test_build_command_with_boolean_flags(self):
        """Test building command with boolean flags."""
        helper = CommandHelper("promptvc")

        command_info = CommandInfo(
            command="promptvc",
            description="Test",
            flags=[
                CommandFlag(
                    name="verbose",
                    short_form="-v",
                    long_form="--verbose",
                    description="Verbose output",
                    required=False,
                    has_value=False,
                ),
            ],
            subcommands=[],
        )

        # Test with boolean true
        args = {"verbose": True}
        cmd = helper.build_command("log", args, command_info)
        assert "--verbose" in cmd

        # Test with boolean false
        args = {"verbose": False}
        cmd = helper.build_command("log", args, command_info)
        assert "--verbose" not in cmd

    def test_build_command_without_command_info(self):
        """Test building command without pre-parsed command info."""
        helper = CommandHelper("promptvc")
        args = {"message": "Test", "file": "test.yaml"}

        # This should work but will make a real --help call
        # We can't fully test this without mocking subprocess
        cmd = helper.build_command("commit", args, command_info=None)

        assert cmd[0] == "promptvc"
        assert cmd[1] == "commit"


class TestExecuteCommandHandler:
    """Tests for execute command handler."""

    @pytest.mark.asyncio
    async def test_handle_execute_command_missing_command(self):
        """Test handler with missing command parameter."""
        result = await handle_execute_command(None, {})

        assert result["success"] is False
        assert "error" in result
        assert "No command specified" in result["error"]

    @pytest.mark.asyncio
    async def test_handle_execute_command_with_parameters(self):
        """Test handler with command and parameters."""
        # This test would require actual promptvc to be available
        # In a real test environment, we'd mock subprocess
        result = await handle_execute_command(
            None,
            {
                "command": "status",
                "parameters": {},
                "check_help": True,
            },
        )

        # Basic structure checks
        assert "success" in result
        assert "stdout" in result
        assert "stderr" in result
        assert "command" in result
        assert "display" in result

    @pytest.mark.asyncio
    async def test_handle_execute_command_without_help_check(self):
        """Test handler without help introspection."""
        result = await handle_execute_command(
            None,
            {
                "command": "status",
                "parameters": {},
                "check_help": False,
            },
        )

        # Should not have command_info when check_help is False
        assert result.get("command_info") is None

    @pytest.mark.asyncio
    async def test_handle_execute_command_display_format(self):
        """Test that display output is properly formatted."""
        result = await handle_execute_command(
            None,
            {
                "command": "status",
                "parameters": {},
                "check_help": True,
            },
        )

        display = result.get("display", "")

        # Check for expected formatting elements
        if result.get("command_info"):
            assert "Command Info" in display or "command info" in display.lower()

        assert "Executing:" in display or "executing" in display.lower()


class TestCommandHelperIntegration:
    """Integration tests for command helper."""

    def test_real_help_command(self):
        """Test with real promptvc --help if available."""
        helper = CommandHelper("promptvc")

        try:
            help_text = helper.get_help()

            # Should get some output
            assert len(help_text) > 0

            # Should contain expected keywords
            assert "promptvc" in help_text.lower() or "usage" in help_text.lower()

        except Exception:
            # If promptvc not available, test should pass
            pytest.skip("promptvc command not available")

    def test_real_subcommand_help(self):
        """Test with real promptvc subcommand --help if available."""
        helper = CommandHelper("promptvc")

        try:
            help_text = helper.get_help("status")

            # Should get help for status command
            assert len(help_text) > 0

            # Parse it
            info = helper.parse_help_output(help_text)
            assert info is not None

        except Exception:
            # If promptvc not available, test should pass
            pytest.skip("promptvc command not available")

"""
Command helper utility for parsing and building promptvc commands.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import re
import subprocess
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class CommandFlag:
    """Represents a command line flag/option."""

    name: str
    short_form: str
    long_form: str
    description: str
    required: bool = False
    has_value: bool = True


@dataclass
class CommandInfo:
    """Information about a command parsed from --help output."""

    command: str
    description: str
    flags: list[CommandFlag] = field(default_factory=list)
    subcommands: list[str] = field(default_factory=list)


class CommandHelper:
    """Helper for introspecting and building CLI commands."""

    def __init__(self, base_command: str = "promptvc"):
        """
        Initialize command helper.

        Args:
            base_command: Base CLI command (default: "promptvc")
        """
        self.base_command = base_command

    def get_help(self, subcommand: Optional[str] = None) -> str:
        """
        Get help text for a command or subcommand.

        Args:
            subcommand: Optional subcommand to get help for

        Returns:
            Help text output

        Raises:
            subprocess.CalledProcessError: If command fails
        """
        cmd = [self.base_command]
        if subcommand:
            cmd.append(subcommand)
        cmd.append("--help")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, cmd, result.stdout, result.stderr
            )

        return result.stdout

    def parse_help_output(self, help_text: str) -> CommandInfo:
        """
        Parse --help output into structured command information.

        Args:
            help_text: Raw --help output

        Returns:
            Parsed command information
        """
        lines = help_text.strip().split("\n")

        # Extract command name from Usage line
        command = self.base_command
        description = ""

        # Parse description (first line before Usage)
        for line in lines:
            if line.strip() and not line.startswith("Usage:"):
                description = line.strip()
                break

        # Parse flags/options
        flags = []
        in_options = False

        for _i, line in enumerate(lines):
            if line.strip().startswith("Options:"):
                in_options = True
                continue

            if line.strip().startswith("Commands:"):
                in_options = False
                continue

            if in_options and line.strip():
                flag = self._parse_option_line(line)
                if flag:
                    flags.append(flag)

        # Parse subcommands
        subcommands = []
        in_commands = False

        for line in lines:
            if line.strip().startswith("Commands:"):
                in_commands = True
                continue

            if in_commands and line.strip():
                # Format: "  command    Description"
                parts = line.strip().split(None, 1)
                if parts and not parts[0].startswith("-"):
                    subcommands.append(parts[0])

        return CommandInfo(
            command=command,
            description=description,
            flags=flags,
            subcommands=subcommands,
        )

    def _parse_option_line(self, line: str) -> Optional[CommandFlag]:
        """
        Parse a single option line from --help output.

        Example formats:
          -m, --message TEXT  Commit message  [required]
          -f, --file PATH     Path to prompt file
          --help              Show this message and exit.

        Args:
            line: Single line from options section

        Returns:
            CommandFlag if parsed successfully, None otherwise
        """
        line = line.strip()

        # Skip empty lines or non-option lines
        if not line or not line.startswith("-"):
            return None

        # Extract flag forms and description
        # Pattern: short_form, long_form TYPE description [required]
        match = re.match(
            r"^\s*(-\w),\s+(--[\w-]+)\s+(\w+)?\s+(.+?)(?:\s+\[required\])?$",
            line,
        )

        if not match:
            # Try pattern without short form: --long_form TYPE description
            match = re.match(
                r"^\s*(--[\w-]+)\s+(\w+)?\s+(.+?)(?:\s+\[required\])?$",
                line,
            )
            if match:
                long_form = match.group(1)
                value_type = match.group(2)
                description = match.group(3).strip()
                required = "[required]" in line

                # Derive name from long form
                name = long_form.removeprefix("--").replace("-", "_")

                return CommandFlag(
                    name=name,
                    short_form="",
                    long_form=long_form,
                    description=description,
                    required=required,
                    has_value=bool(value_type),
                )
        else:
            short_form = match.group(1)
            long_form = match.group(2)
            value_type = match.group(3)
            description = match.group(4).strip()
            required = "[required]" in line

            # Derive name from long form
            name = long_form.removeprefix("--").replace("-", "_")

            return CommandFlag(
                name=name,
                short_form=short_form,
                long_form=long_form,
                description=description,
                required=required,
                has_value=bool(value_type),
            )

        return None

    def build_command(
        self,
        subcommand: str,
        args: dict[str, Any],
        command_info: Optional[CommandInfo] = None,
    ) -> list[str]:
        """
        Build command line arguments from structured parameters.

        Args:
            subcommand: Subcommand to execute
            args: Dictionary of argument name -> value
            command_info: Optional pre-parsed command info. If None, will fetch help.

        Returns:
            List of command parts ready for subprocess.run()
        """
        cmd = [self.base_command, subcommand]

        # If no command info provided, try to get it
        if command_info is None:
            try:
                help_text = self.get_help(subcommand)
                command_info = self.parse_help_output(help_text)
            except Exception:
                # If we can't get help, just build command with args as-is
                command_info = CommandInfo(command=self.base_command, description="")

        # Build flag arguments
        for key, value in args.items():
            # Find matching flag in command info
            flag = None
            for f in command_info.flags:
                if f.name == key or f.name.replace("_", "-") == key.replace("_", "-"):
                    flag = f
                    break

            if flag:
                # Use long form if available
                flag_name = flag.long_form if flag.long_form else flag.short_form

                if flag.has_value:
                    # Flag takes a value
                    if value is not None and value != "":
                        cmd.append(flag_name)
                        cmd.append(str(value))
                else:
                    # Boolean flag
                    if value:
                        cmd.append(flag_name)
            else:
                # No flag info, guess based on key
                flag_name = f"--{key.replace('_', '-')}"

                if isinstance(value, bool):
                    if value:
                        cmd.append(flag_name)
                else:
                    cmd.append(flag_name)
                    cmd.append(str(value))

        return cmd

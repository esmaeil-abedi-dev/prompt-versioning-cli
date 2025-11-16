"""
Shared utility for checking command help before execution.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import subprocess
from typing import Optional


def check_command_help(command: str) -> Optional[dict]:
    """
    Check command --help before execution.

    Args:
        command: The subcommand to check (e.g., 'commit', 'init', 'log')

    Returns:
        Dictionary with help information or None if failed
    """
    try:
        result = subprocess.run(
            ["promptvc", command, "--help"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            # Extract just the options section for preview
            help_output = result.stdout
            options_preview = []

            if "Options:" in help_output:
                options_section = help_output.split("Options:")[1]
                # Get first few lines of options
                for line in options_section.split("\n")[:8]:
                    if line.strip() and not line.startswith("Usage:"):
                        options_preview.append(line)

            return {
                "command": f"promptvc {command}",
                "help_output": help_output,
                "options_preview": options_preview,
                "checked": True,
            }
    except Exception as e:
        return {
            "command": f"promptvc {command}",
            "error": f"Could not fetch help: {str(e)}",
            "checked": False,
        }

    return None


def format_help_display(help_info: dict, success_message: str = "") -> str:
    """
    Format help info for display.

    Args:
        help_info: Help information dictionary
        success_message: Additional success message to append

    Returns:
        Formatted display string
    """
    if not help_info:
        return success_message

    parts = []

    if help_info.get("checked"):
        parts.append("📚 Command Help Checked First")
        parts.append(f"Command: {help_info.get('command', 'unknown')}")

        if help_info.get("options_preview"):
            parts.append("\nAvailable Options:")
            for option_line in help_info["options_preview"]:
                parts.append(option_line)

        parts.append("\n" + "=" * 60 + "\n")
    elif help_info.get("error"):
        parts.append(f"⚠️ Help check failed: {help_info['error']}\n")

    if success_message:
        parts.append(success_message)

    return "\n".join(parts)

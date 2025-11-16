"""
Generic command execution handler for MCP server.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import subprocess
from typing import Any

from .command_helper import CommandHelper


async def handle_execute_command(
    _request: Any,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute a promptvc command with optional help introspection.

    Args:
        _request: MCP request object (unused)
        arguments: Command arguments containing:
            - command: Subcommand to execute (required)
            - parameters: Dictionary of command parameters (optional)
            - check_help: Whether to check --help first (optional, default: False)

    Returns:
        Dictionary with execution results:
            - success: Whether command succeeded
            - stdout: Command stdout
            - stderr: Command stderr
            - returncode: Command exit code
            - command: Full command that was executed
            - command_info: Parsed command info (if check_help=True)
            - display: Formatted output for display
            - error: Error message (if failed)
    """
    command = arguments.get("command")
    parameters = arguments.get("parameters", {})
    check_help = arguments.get("check_help", False)

    if not command:
        return {
            "success": False,
            "error": "No command specified",
            "stdout": "",
            "stderr": "",
            "returncode": -1,
            "command": "",
            "display": "❌ Error: No command specified",
        }

    helper = CommandHelper("promptvc")
    command_info = None

    # Optionally check help first
    if check_help:
        try:
            help_text = helper.get_help(command)
            command_info = helper.parse_help_output(help_text)
        except Exception:
            # Help check failed, but continue with execution
            pass

    # Build command
    try:
        cmd_parts = helper.build_command(command, parameters, command_info)
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to build command: {str(e)}",
            "stdout": "",
            "stderr": "",
            "returncode": -1,
            "command": f"promptvc {command}",
            "display": f"❌ Error building command: {str(e)}",
        }

    # Execute command
    try:
        result = subprocess.run(
            cmd_parts,
            capture_output=True,
            text=True,
            timeout=30,
        )

        success = result.returncode == 0
        cmd_str = " ".join(cmd_parts)

        # Build display output
        display_parts = []

        if command_info:
            display_parts.append("📚 Command Info Checked")
            display_parts.append(f"Command: {command_info.command} {command}")
            if command_info.flags:
                display_parts.append(f"Available flags: {len(command_info.flags)} options")
            display_parts.append("")

        display_parts.append(f"Executing: {cmd_str}")
        display_parts.append("")

        if success:
            display_parts.append("✅ Command executed successfully")
            if result.stdout:
                display_parts.append("\nOutput:")
                display_parts.append(result.stdout)
        else:
            display_parts.append(f"❌ Command failed (exit code: {result.returncode})")
            if result.stderr:
                display_parts.append("\nError output:")
                display_parts.append(result.stderr)

        display = "\n".join(display_parts)

        response = {
            "success": success,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "command": cmd_str,
            "display": display,
        }

        if command_info:
            response["command_info"] = {
                "command": command_info.command,
                "description": command_info.description,
                "flags": [
                    {
                        "name": f.name,
                        "short_form": f.short_form,
                        "long_form": f.long_form,
                        "description": f.description,
                        "required": f.required,
                    }
                    for f in command_info.flags
                ],
                "subcommands": command_info.subcommands,
            }

        return response

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out after 30 seconds",
            "stdout": "",
            "stderr": "",
            "returncode": -1,
            "command": " ".join(cmd_parts),
            "display": "❌ Error: Command timed out after 30 seconds",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to execute command: {str(e)}",
            "stdout": "",
            "stderr": "",
            "returncode": -1,
            "command": " ".join(cmd_parts),
            "display": f"❌ Error executing command: {str(e)}",
        }

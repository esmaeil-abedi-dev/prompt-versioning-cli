"""
Command execution utilities for CLI.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import subprocess

import click


def execute_shell_command(command: str) -> None:
    """
    Execute a shell command and display output.

    Args:
        command: Shell command to execute
    """
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.stdout:
            click.echo(result.stdout)

        if result.stderr:
            click.echo(result.stderr, err=True)

        if result.returncode != 0:
            click.echo(f"Command exited with code {result.returncode}", err=True)

    except Exception as e:
        click.echo(f"✗ Execution failed: {e}", err=True)

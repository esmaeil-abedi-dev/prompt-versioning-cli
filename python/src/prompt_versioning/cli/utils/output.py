"""
Output formatting utilities for CLI.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import sys
from typing import NoReturn

import click


def success(message: str) -> None:
    """Print success message."""
    click.echo(f"✓ {message}")


def error(message: str, exit_code: int = 1) -> NoReturn:
    """Print error message and exit."""
    click.echo(f"✗ {message}", err=True)
    sys.exit(exit_code)


def warning(message: str) -> None:
    """Print warning message."""
    click.echo(f"⚠️  {message}", err=True)


def info(message: str) -> None:
    """Print info message."""
    click.echo(message)


def section(title: str) -> None:
    """Print section header."""
    click.echo(f"\n{title}\n")

"""
Init command - Initialize a new prompt repository.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from pathlib import Path

import click

from ..core import init_repository
from ..utils import error, success


@click.command()
@click.option("--path", default=".", help="Repository path (default: current directory)")
def init(path: str) -> None:
    """Initialize a new prompt repository."""
    try:
        init_repository(path)
        success(f"Initialized prompt repository in {Path(path).resolve()}/.promptvc/")
    except FileExistsError as e:
        error(str(e))

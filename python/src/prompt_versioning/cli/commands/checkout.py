"""
Checkout command - Checkout a specific commit.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import json
from pathlib import Path
from typing import Optional

import click
import yaml

from ..core import get_repository
from ..utils import error


@click.command()
@click.argument("commit_ref")
@click.argument("file_path", required=False)
@click.option("--path", default=".", help="Repository path")
@click.option("--output", "-o", help="Write prompt to specific file")
@click.option("--no-write", is_flag=True, help="Don't write to file, just show info")
def checkout(commit_ref: str, file_path: Optional[str], path: str, output: Optional[str], no_write: bool):
    """Checkout a specific commit.

    FILE_PATH: Optional file to write the checked-out prompt to.
    If not specified and --no-write is not set, will prompt for filename.
    """
    try:
        repo = get_repository(path)
        version = repo.checkout(commit_ref)

        click.echo(f"✓ Checked out commit {version.commit.short_hash()}")
        click.echo(f"  {version.commit.message}")

        # Determine output file
        output_file = output or file_path

        # Write prompt to file unless --no-write is specified
        if not no_write:
            if not output_file:
                # Prompt for filename if not provided
                output_file = click.prompt("Enter filename to write prompt", default="prompt.yaml")

            output_path = Path(output_file)
            prompt_data = version.prompt.model_dump(exclude_none=True)

            if output_file.endswith(".json"):
                output_path.write_text(json.dumps(prompt_data, indent=2))
            else:
                output_path.write_text(yaml.dump(prompt_data, sort_keys=False))

            click.echo(f"✓ Wrote prompt to {output_file}")

    except ValueError as e:
        error(str(e))

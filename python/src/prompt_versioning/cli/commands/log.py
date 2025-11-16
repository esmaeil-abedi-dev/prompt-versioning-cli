"""
Log command - Show commit history.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from typing import Optional

import click

from ..core import get_repository


@click.command()
@click.option("--max-count", "-n", type=int, help="Limit number of commits")
@click.option("--oneline", is_flag=True, help="Show condensed output")
@click.option("--path", default=".", help="Repository path")
def log(max_count: Optional[int], oneline: bool, path: str):
    """Show commit history."""
    repo = get_repository(path)
    versions = repo.log(max_count)

    if not versions:
        click.echo("No commits yet")
        return

    for version in versions:
        if oneline:
            click.echo(f"{version.commit.short_hash()} {version.commit.message}")
        else:
            click.echo(f"commit {version.commit.hash}")
            click.echo(f"Author: {version.commit.author}")
            click.echo(f"Date: {version.commit.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

            if version.commit.tags:
                click.echo(f"Tags: {', '.join(version.commit.tags)}")

            click.echo(f"\n    {version.commit.message}\n")

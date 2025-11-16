"""
Status command - Show repository status.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import click

from ..core import get_repository


@click.command()
@click.option("--path", default=".", help="Repository path")
def status(path: str):
    """Show repository status."""
    repo = get_repository(path)

    if not repo.exists():
        click.echo("✗ Not a prompt repository (run 'promptvc init')")
        click.secho("Run: promptvc init", fg="yellow")
        return

    current = repo.get_current_version()

    if not current:
        click.echo("No commits yet")
        return

    click.echo("Current version:")
    click.echo(f"  Commit: {current.commit.short_hash()}")
    click.echo(f"  Message: {current.commit.message}")
    click.echo(f"  Author: {current.commit.author}")
    click.echo(f"  Date: {current.commit.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

    if current.commit.tags:
        click.echo(f"  Tags: {', '.join(current.commit.tags)}")

"""
Tags command - List all experiment tags.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import json

import click

from ..utils import ensure_repository


@click.command()
@click.option("--path", default=".", help="Repository path")
def tags(path: str) -> None:
    """List all tags."""
    repo = ensure_repository(path)
    tag_list = repo.list_tags()

    if not tag_list:
        click.echo("No tags yet")
        return

    for tag_obj in sorted(tag_list, key=lambda t: t.created_at, reverse=True):
        click.echo(f"{tag_obj.name} -> {tag_obj.commit_hash[:7]}")

        if tag_obj.metadata:
            click.echo(f"  Metadata: {json.dumps(tag_obj.metadata, indent=2)}")

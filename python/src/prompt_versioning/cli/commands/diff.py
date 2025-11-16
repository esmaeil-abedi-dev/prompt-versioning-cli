"""
Diff command - Show differences between commits.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import click

from ..core import get_repository
from ..utils import error


@click.command()
@click.argument("commit1")
@click.argument("commit2")
@click.option("--path", default=".", help="Repository path")
@click.option("--summary", is_flag=True, help="Show only summary")
def diff(commit1: str, commit2: str, path: str, summary: bool):
    """Show differences between two commits."""
    try:
        repo = get_repository(path)
        diff_result = repo.diff(commit1, commit2)

        if summary:
            click.echo(diff_result.format_summary())
        else:
            click.echo(diff_result.format())

    except ValueError as e:
        error(str(e))

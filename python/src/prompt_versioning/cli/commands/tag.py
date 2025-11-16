"""
Tag command - Create experiment tags.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import json
from typing import Optional

import click

from ..core import get_repository
from ..utils import error, parse_json_string


@click.command()
@click.argument("tag_name")
@click.argument("commit_hash", required=False)
@click.option("--commit", "commit_option", help="Commit to tag (default: HEAD)")
@click.option("--metadata", help="Experiment metadata (JSON string)")
@click.option("--path", default=".", help="Repository path")
def tag(tag_name: str, commit_hash: Optional[str], commit_option: Optional[str], metadata: Optional[str], path: str):
    """Create a tag for an experiment.

    COMMIT_HASH can be provided as a positional argument or via --commit option.
    If neither is provided, tags HEAD.
    """
    try:
        # Use commit_option if provided, otherwise use commit_hash argument
        commit = commit_option or commit_hash

        # Parse metadata if provided
        metadata_dict = None
        if metadata:
            metadata_dict = parse_json_string(metadata, "metadata")

        repo = get_repository(path)
        tag_obj = repo.tag(tag_name, commit, metadata_dict)

        click.echo(f"✓ Tagged {tag_obj.commit_hash[:7]} as '{tag_name}'")

        if metadata_dict:
            click.echo(f"  Metadata: {json.dumps(metadata_dict, indent=2)}")

    except ValueError as e:
        error(str(e))

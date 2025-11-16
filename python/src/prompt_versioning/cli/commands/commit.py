"""
Commit command - Create a new commit with a prompt.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import click

from ..core import get_repository
from ..utils import error, parse_prompt_file


@click.command()
@click.argument("file_path", required=False)
@click.option("-m", "--message", required=True, help="Commit message")
@click.option("-f", "--file", "file_option", required=False, help="Prompt file (YAML or JSON)")
@click.option("--author", default="system", help="Commit author")
@click.option("--path", default=".", help="Repository path")
def commit(file_path: str, message: str, file_option: str, author: str, path: str):
    """Create a new commit with the given prompt.
    
    FILE_PATH can be provided as a positional argument or via -f/--file option.
    """
    try:
        # Use file_option if provided, otherwise use file_path argument
        prompt_file = file_option or file_path
        
        if not prompt_file:
            error("Missing prompt file. Provide as argument or use -f/--file option.")
            return
        
        # Parse prompt file
        prompt_data, _ = parse_prompt_file(prompt_file)

        # Create commit
        repo = get_repository(path)
        commit_obj = repo.commit(message, prompt_data, author)

        # Get branch name (always "main" for now)
        branch = "main"

        click.echo(f"[{branch} {commit_obj.short_hash()}] {message}")

    except ValueError as e:
        error(str(e))

"""
Main CLI application - orchestrates all commands.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import click

from .commands import (
    agent,
    audit,
    checkout,
    commit,
    create_prompt,
    diff,
    init,
    log,
    mcp_server,
    mcp_setup,
    status,
    tag,
    tags,
)


@click.group()
@click.version_option(version="1.0.0", prog_name="promptvc")
def cli() -> None:
    """
    Prompt Version Control - Git-like version control for LLM prompts.

    Track changes, compare versions, and maintain audit trails for your prompts.
    """
    pass


# Register all commands
cli.add_command(init)
cli.add_command(commit)
cli.add_command(log)
cli.add_command(diff)
cli.add_command(checkout)
cli.add_command(tag)
cli.add_command(tags)
cli.add_command(status)
cli.add_command(audit)
cli.add_command(agent)
cli.add_command(create_prompt)
cli.add_command(mcp_server)
cli.add_command(mcp_setup)


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()

"""
Audit command - Generate compliance audit logs.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from pathlib import Path
from typing import Optional

import click

from ..core import get_repository
from ..utils import success


@click.command()
@click.option(
    "--format",
    "format_type",
    type=click.Choice(["json", "csv"], case_sensitive=False),
    default="json",
    help="Output format",
)
@click.option("--output", "-o", help="Output file path")
@click.option("--path", default=".", help="Repository path")
def audit(format_type: str, output: Optional[str], path: str):
    """Generate compliance audit log."""
    repo = get_repository(path)
    audit_data = repo.audit_log(format=format_type.lower())

    if output:
        Path(output).write_text(audit_data)
        success(f"Exported audit log to {output}")
    else:
        click.echo(audit_data)

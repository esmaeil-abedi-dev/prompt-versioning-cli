"""
Audit command - Generate compliance audit logs.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import json
from pathlib import Path
from typing import Optional

import click

from ..utils import ensure_repository, success


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
def audit(format_type: str, output: Optional[str], path: str) -> None:
    """Generate compliance audit log."""
    repo = ensure_repository(path)
    audit_data = repo.audit_log(format=format_type.lower())

    # Convert to string if necessary
    audit_str = audit_data if isinstance(audit_data, str) else json.dumps(audit_data, indent=2)

    if output:
        Path(output).write_text(audit_str)
        success(f"Exported audit log to {output}")
    else:
        click.echo(audit_str)

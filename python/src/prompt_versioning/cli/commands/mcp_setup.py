"""
MCP Setup command - Generate MCP server configuration files.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import json
import sys
from pathlib import Path
from typing import Optional

import click

from ..utils import error, info, success


@click.command(name="mcp-setup")
@click.option(
    "--ide",
    type=click.Choice(["vscode", "claude", "zed"], case_sensitive=False),
    required=True,
    help="IDE to configure",
)
@click.option("--path", default=".", help="Repository path (default: current directory)")
@click.option("--output", "-o", help="Output file path (default: IDE-specific location)")
@click.option("--init", is_flag=True, help="Initialize repository if it doesn't exist")
def mcp_setup(ide: str, path: str, output: Optional[str], init: bool):
    """
    Generate MCP server configuration files for different IDEs.

    Automatically creates the correct configuration format for:
    - VSCode (.vscode/mcp-config.json)
    - Claude Desktop (claude_desktop_config.json)
    - Zed (.config/zed/settings.json)

    Examples:

        # Generate VSCode config (will warn if repository doesn't exist)
        promptvc mcp-setup --ide vscode

        # Generate config AND initialize repository
        promptvc mcp-setup --ide vscode --init

        # Generate Claude Desktop config
        promptvc mcp-setup --ide claude

        # Custom repository location
        promptvc mcp-setup --ide vscode --path ./my-prompts

        # Custom output location
        promptvc mcp-setup --ide vscode -o ./my-config.json
    """
    try:
        # Resolve repository path
        repo_path = Path(path).resolve()

        # Check if repository exists
        from ...core import PromptRepository
        repo_exists = (repo_path / ".promptvc").exists()
        
        if not repo_exists:
            if init:
                # Auto-initialize the repository
                try:
                    PromptRepository.init(repo_path)
                    success(f"Initialized repository at {repo_path}/.promptvc/")
                    repo_exists = True
                except Exception as e:
                    error(f"Failed to initialize repository: {e}")
                    return
            else:
                # Warn but continue - MCP server can initialize later
                click.echo(f"⚠️  Repository not found at {repo_path}/.promptvc/")
                click.echo(f"   You can initialize it later with: promptvc init --path {repo_path}")
                click.echo(f"   Or ask Copilot: @workspace /prompt-version initialize repository")
                click.echo()

        # Generate configuration based on IDE
        if ide == "vscode":
            config = _generate_vscode_config(repo_path)
            default_output = Path(".vscode/mcp-config.json")
            config_type = "VSCode MCP"

        elif ide == "claude":
            config = _generate_claude_config(repo_path)
            if sys.platform == "darwin":  # macOS
                default_output = (
                    Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
                )
            elif sys.platform == "win32":  # Windows
                default_output = Path.home() / "AppData/Roaming/Claude/claude_desktop_config.json"
            else:  # Linux
                default_output = Path.home() / ".config/claude/claude_desktop_config.json"
            config_type = "Claude Desktop MCP"

        elif ide == "zed":
            config = _generate_zed_config(repo_path)
            default_output = Path.home() / ".config/zed/settings.json"
            config_type = "Zed MCP"

        # Determine output path
        output_path = Path(output) if output else default_output

        # Create directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write configuration
        output_path.write_text(json.dumps(config, indent=2))

        success(f"Generated {config_type} configuration")
        info(f"  Location: {output_path}")
        info(f"  Repository: {repo_path}")

        # Print next steps
        click.echo("\n📝 Next Steps:")
        if ide == "vscode":
            click.echo("  1. Reload VSCode window (Cmd+Shift+P → 'Developer: Reload Window')")
            if not repo_exists:
                click.echo("  2. Ask Copilot: @workspace /prompt-version initialize repository")
                click.echo("  3. Ask Copilot: @workspace /prompt-version status")
            else:
                click.echo("  2. Ask Copilot: @workspace /prompt-version status")
                click.echo("  3. Start using prompt versioning with Copilot!")
        elif ide == "claude":
            click.echo("  1. Restart Claude Desktop")
            click.echo("  2. Check for 🔌 icon showing MCP connection")
            if not repo_exists:
                click.echo("  3. Ask Claude to initialize the prompt repository")
            else:
                click.echo("  3. Ask Claude to use prompt versioning tools")
        elif ide == "zed":
            click.echo("  1. Restart Zed editor")
            if not repo_exists:
                click.echo("  2. Initialize: /prompt-version init")
            click.echo("  2. Use /prompt-version commands in assistant panel")

    except Exception as e:
        error(f"Failed to generate configuration: {e}")


def _generate_vscode_config(repo_path: Path) -> dict:
    """Generate VSCode MCP configuration."""
    return {
        "mcpServers": {
            "promptvc": {
                "command": "python",
                "args": ["-m", "prompt_versioning.cli", "mcp-server", "--path", str(repo_path)],
                "env": {"PROMPTVC_MCP_TOKEN": "${env:PROMPTVC_MCP_TOKEN}"},
            }
        }
    }


def _generate_claude_config(repo_path: Path) -> dict:
    """Generate Claude Desktop MCP configuration."""
    return {
        "mcpServers": {
            "promptvc": {
                "command": "python",
                "args": ["-m", "prompt_versioning.cli", "mcp-server", "--path", str(repo_path)],
                "env": {"PROMPTVC_MCP_TOKEN": ""},
            }
        }
    }


def _generate_zed_config(repo_path: Path) -> dict:
    """Generate Zed MCP configuration."""
    return {
        "context_servers": {
            "promptvc": {
                "command": {
                    "path": "python",
                    "args": ["-m", "prompt_versioning.cli", "mcp-server", "--path", str(repo_path)],
                }
            }
        }
    }

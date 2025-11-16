"""
MCP server command - Start Model Context Protocol server.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from pathlib import Path
from typing import Optional

import click

from ..utils import error


@click.command(name="mcp-server")
@click.option("--path", default=".promptvc", help="Repository path (default: .promptvc)")
@click.option(
    "--transport", type=click.Choice(["stdio", "http"]), default="stdio", help="Transport protocol"
)
@click.option("--host", default="127.0.0.1", help="Host for HTTP transport (default: 127.0.0.1)")
@click.option("--port", type=int, default=8080, help="Port for HTTP transport (default: 8080)")
@click.option("--auth-token", help="Authentication token (or set PROMPTVC_MCP_TOKEN env var)")
def mcp_server(path: str, transport: str, host: str, port: int, auth_token: Optional[str]):
    """
    Start the Model Context Protocol (MCP) server.

    The MCP server exposes all prompt versioning operations as MCP-compatible
    tools that can be used by VSCode Copilot, Claude Desktop, and other MCP clients.

    Examples:

        # Start server with stdio transport (for VSCode/Copilot):
        promptvc mcp-server

        # Start server with custom repository path:
        promptvc mcp-server --path /path/to/.promptvc

        # Start HTTP server for remote access:
        promptvc mcp-server --transport http --port 8080

        # Start with authentication:
        export PROMPTVC_MCP_TOKEN="your-token"
        promptvc mcp-server
    """
    try:
        import asyncio

        from ...mcp import PromptVCMCPServer

        click.echo("🚀 Starting Prompt Version Control MCP Server...")
        click.echo(f"   Repository: {Path(path).resolve()}")
        click.echo(f"   Transport: {transport}")

        if auth_token:
            click.echo("   Authentication: Enabled")

        # Create server
        server = PromptVCMCPServer(repo_path=Path(path), auth_token=auth_token)

        # Run server based on transport
        if transport == "stdio":
            click.echo("\n✓ Server running on stdio (press Ctrl+C to stop)")
            asyncio.run(server.run_stdio())

        elif transport == "http":
            click.echo(f"\n✓ Server running on http://{host}:{port} (press Ctrl+C to stop)")
            asyncio.run(server.run_http(host=host, port=port))

    except ImportError as e:
        error(
            f"MCP server dependencies not installed: {e}\n"
            "Install with: pip install prompt-versioning-cli[agent]"
        )

    except KeyboardInterrupt:
        click.echo("\n\n👋 Server stopped")

    except Exception as e:
        error(f"Server error: {e}")

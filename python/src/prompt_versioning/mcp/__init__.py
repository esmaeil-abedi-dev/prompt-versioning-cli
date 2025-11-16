"""
Model Context Protocol (MCP) server for prompt versioning.

Exposes prompt version management operations as MCP-compatible tools,
enabling integration with VSCode Copilot and other MCP clients.

MCP Protocol: https://modelcontextprotocol.io/
Specification: JSON-RPC 2.0 over stdio or HTTP

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from .protocol import (
    MCPError,
    MCPRequest,
    MCPResource,
    MCPResponse,
    MCPTool,
    PromptVCMCPServer,
    main,
)

__all__ = [
    "MCPRequest",
    "MCPResponse",
    "MCPTool",
    "MCPResource",
    "MCPError",
    "PromptVCMCPServer",
    "main",
]

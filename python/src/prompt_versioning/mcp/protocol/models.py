"""
Model Context Protocol (MCP) data models and exceptions.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class MCPRequest:
    """MCP JSON-RPC 2.0 request."""

    jsonrpc: str = "2.0"
    id: Optional[Any] = None
    method: str = ""
    params: Optional[dict[str, Any]] = None


@dataclass
class MCPResponse:
    """MCP JSON-RPC 2.0 response."""

    jsonrpc: str = "2.0"
    id: Optional[Any] = None
    result: Optional[Any] = None
    error: Optional[dict[str, Any]] = None


@dataclass
class MCPTool:
    """MCP tool definition."""

    name: str
    description: str
    inputSchema: dict[str, Any]


@dataclass
class MCPResource:
    """MCP resource definition."""

    uri: str
    name: str
    description: str
    mimeType: str = "application/json"


class MCPError(Exception):
    """Base exception for MCP errors."""

    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)

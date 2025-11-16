"""
MCP server implementation for prompt versioning.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import asyncio
import json
import logging
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable, Optional

from ...core import PromptRepository
from ..handlers import (
    handle_checkout_version,
    handle_commit_prompt,
    handle_diff_versions,
    handle_generate_audit,
    handle_get_history,
    handle_get_status,
    handle_init_repository,
    handle_list_tags,
    handle_rollback,
    handle_tag_experiment,
)
from .models import MCPError, MCPRequest, MCPResponse
from .resources import get_resource_definitions
from .tools import get_tool_definitions

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PromptVCMCPServer:
    """
    MCP server for prompt versioning operations.

    Exposes tools for:
    - Initializing repositories
    - Committing prompts
    - Viewing history
    - Comparing versions
    - Checking out versions
    - Tagging experiments
    - Generating audit logs
    """

    # Standard JSON-RPC error codes
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

    # Custom error codes
    AUTH_ERROR = -32001

    def __init__(self, repo_path: str = ".", auth_token: Optional[str] = None):
        """
        Initialize MCP server.

        Args:
            repo_path: Path to prompt repository
            auth_token: Optional authentication token for security
        """
        self.repo_path = Path(repo_path)
        self.auth_token = auth_token or os.getenv("PROMPTVC_MCP_TOKEN")
        self.repo: Optional[PromptRepository] = None

        # Handler registry
        self.handlers: dict[str, Callable] = {
            # MCP protocol methods
            "initialize": self.handle_initialize,
            "tools/list": self.handle_tools_list,
            "tools/call": self.handle_tools_call,
            "resources/list": self.handle_resources_list,
            "resources/read": self.handle_resources_read,
            # Utility methods
            "ping": self.handle_ping,
        }

        # Tool handlers
        self.tool_handlers: dict[str, Callable] = {
            "promptvc_init_repository": lambda args: handle_init_repository(self.repo, args, self.repo_path, self),
            "promptvc_commit": lambda args: handle_commit_prompt(self.repo, args),
            "promptvc_get_history": lambda args: handle_get_history(self.repo, args),
            "promptvc_diff": lambda args: handle_diff_versions(self.repo, args),
            "promptvc_checkout": lambda args: handle_checkout_version(self.repo, args),
            "promptvc_tag": lambda args: handle_tag_experiment(self.repo, args),
            "promptvc_list_tags": lambda args: handle_list_tags(self.repo, args),
            "promptvc_get_status": lambda args: handle_get_status(self.repo, args),
            "promptvc_generate_audit": lambda args: handle_generate_audit(self.repo, args),
            "promptvc_rollback": lambda args: handle_rollback(self.repo, args),
        }

        # Initialize repository if exists
        try:
            self.repo = PromptRepository(repo_path)
            if not self.repo.exists():
                self.repo = None
        except Exception:
            self.repo = None

    # ==================== MCP Protocol Handlers ====================

    async def handle_initialize(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle MCP initialize request."""
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "prompt-versioning-mcp", "version": "1.0.0"},
            "capabilities": {"tools": {}, "resources": {}},
        }

    async def handle_tools_list(self, params: dict[str, Any]) -> dict[str, Any]:
        """List all available tools."""
        return {"tools": get_tool_definitions()}

    async def handle_tools_call(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute a tool."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name not in self.tool_handlers:
            raise MCPError(self.INVALID_PARAMS, f"Tool not found: {tool_name}")

        handler = self.tool_handlers[tool_name]
        result = await handler(arguments)

        return result

    async def handle_resources_list(self, params: dict[str, Any]) -> dict[str, Any]:
        """List available resources."""
        return {"resources": get_resource_definitions()}

    async def handle_resources_read(self, params: dict[str, Any]) -> dict[str, Any]:
        """Read a resource."""
        uri = params.get("uri", "")

        if uri == "promptvc://status":
            result = await self.tool_handlers["promptvc_get_status"]({})
        elif uri == "promptvc://history":
            result = await self.tool_handlers["promptvc_get_history"]({})
        elif uri == "promptvc://tags":
            result = await self.tool_handlers["promptvc_list_tags"]({})
        else:
            raise MCPError(self.INVALID_PARAMS, f"Unknown resource URI: {uri}")

        return {
            "contents": [
                {"uri": uri, "mimeType": "application/json", "text": json.dumps(result, indent=2)}
            ]
        }

    async def handle_ping(self, params: dict[str, Any]) -> dict[str, Any]:
        """Health check."""
        return {}

    # ==================== Request Processing ====================

    def _authenticate(self, request: MCPRequest) -> bool:
        """Verify authentication if token is set."""
        if not self.auth_token:
            return True

        # Check for auth token in params (support both 'token' and '_auth_token')
        if request.params:
            token = request.params.get("token") or request.params.get("_auth_token")
            return token == self.auth_token

        return False

    async def process_request(self, request_data: dict[str, Any]) -> MCPResponse:
        """Process a single MCP request."""
        try:
            # Check for required fields before creating MCPRequest
            if "method" not in request_data:
                return MCPResponse(
                    id=request_data.get("id"),
                    error={"code": self.INVALID_REQUEST, "message": "Missing required field: method"}
                )

            request = MCPRequest(**request_data)
        except Exception as e:
            return MCPResponse(
                error={"code": self.INVALID_REQUEST, "message": f"Invalid request format: {e}"}
            )

        # Authenticate
        if not self._authenticate(request):
            return MCPResponse(
                id=request.id,
                error={"code": self.AUTH_ERROR, "message": "Authentication failed"},
            )

        # Find handler
        if request.method not in self.handlers:
            return MCPResponse(
                id=request.id,
                error={
                    "code": self.METHOD_NOT_FOUND,
                    "message": f"Method not found: {request.method}",
                },
            )

        # Execute handler
        try:
            handler = self.handlers[request.method]
            result = await handler(request.params or {})

            return MCPResponse(id=request.id, result=result)
        except MCPError as e:
            return MCPResponse(
                id=request.id, error={"code": e.code, "message": e.message, "data": e.data}
            )
        except Exception as e:
            logger.exception("Handler error")
            return MCPResponse(
                id=request.id, error={"code": self.INTERNAL_ERROR, "message": str(e)}
            )

    def handle_request(self, request_json: str) -> str:
        """
        Synchronous wrapper for handling requests (for testing).

        Args:
            request_json: JSON string containing the request

        Returns:
            JSON string containing the response
        """
        try:
            request_data = json.loads(request_json)
        except json.JSONDecodeError as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": self.PARSE_ERROR, "message": f"Parse error: {e}"},
            }
            return json.dumps(error_response)

        # Run async process_request in sync context
        response = asyncio.run(self.process_request(request_data))

        # Convert response to dict
        response_dict = {"jsonrpc": response.jsonrpc, "id": response.id}

        if response.result is not None:
            response_dict["result"] = response.result
        if response.error is not None:
            response_dict["error"] = response.error

        return json.dumps(response_dict)

    async def run_stdio(self):
        """Run server in stdio mode."""
        logger.info("MCP server starting in stdio mode")

        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)

                if not line:
                    break

                request_data = json.loads(line.strip())
                response = await self.process_request(request_data)

                # Convert response to dict
                response_dict = {"jsonrpc": response.jsonrpc, "id": response.id}

                if response.result is not None:
                    response_dict["result"] = response.result
                if response.error is not None:
                    response_dict["error"] = response.error

                print(json.dumps(response_dict), flush=True)

            except json.JSONDecodeError as e:
                error_response = MCPResponse(
                    error={"code": self.PARSE_ERROR, "message": f"Parse error: {e}"}
                )
                print(json.dumps(asdict(error_response)), flush=True)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.exception("Server error")
                error_response = MCPResponse(error={"code": self.INTERNAL_ERROR, "message": str(e)})
                print(json.dumps(asdict(error_response)), flush=True)

        logger.info("MCP server shutting down")


def main():
    """Entry point for MCP server."""
    import argparse

    parser = argparse.ArgumentParser(description="PromptVC MCP Server")
    parser.add_argument("--path", default=".", help="Repository path")
    parser.add_argument(
        "--transport", choices=["stdio"], default="stdio", help="Transport mode (default: stdio)"
    )
    parser.add_argument("--auth-token", help="Authentication token")

    args = parser.parse_args()

    server = PromptVCMCPServer(
        repo_path=args.path, auth_token=args.auth_token or os.getenv("PROMPTVC_MCP_TOKEN")
    )

    asyncio.run(server.run_stdio())


if __name__ == "__main__":
    main()

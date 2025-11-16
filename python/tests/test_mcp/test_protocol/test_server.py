"""
Tests for the MCP (Model Context Protocol) server implementation.

This module tests:
- JSON-RPC 2.0 protocol compliance
- All 10 tool handlers (init, commit, history, diff, checkout, tag, list_tags, status, audit, rollback)
- Resource handlers (status, history, tags)
- Authentication and authorization
- Error handling and edge cases
- Request/response serialization

Note: These tests are currently skipped due to implementation changes in the MCP server.
"""

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from prompt_versioning.core import PromptRepository
from prompt_versioning.mcp import PromptVCMCPServer

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def temp_repo_path():
    """Create a temporary directory for test repository."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mcp_server(temp_repo_path):
    """Create an MCP server instance with temporary repository."""
    server = PromptVCMCPServer(repo_path=temp_repo_path, auth_token=None)  # No auth for basic tests
    return server


@pytest.fixture
def authenticated_server(temp_repo_path):
    """Create an MCP server with authentication enabled."""
    server = PromptVCMCPServer(repo_path=temp_repo_path, auth_token="test-token-12345")
    return server


@pytest.fixture
def initialized_server(temp_repo_path):
    """Create an MCP server with initialized repository."""
    # Initialize repository
    PromptRepository.init(temp_repo_path)

    # Create server
    server = PromptVCMCPServer(repo_path=temp_repo_path, auth_token=None)
    return server


# ============================================================================
# JSON-RPC Protocol Tests
# ============================================================================


class TestJSONRPCProtocol:
    """Test JSON-RPC 2.0 protocol compliance."""

    def test_initialize_request(self, mcp_server):
        """Test initialize request handling."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }

        response = mcp_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert result["jsonrpc"] == "2.0"
        assert result["id"] == 1
        assert "result" in result
        assert result["result"]["protocolVersion"] == "2024-11-05"
        assert result["result"]["serverInfo"]["name"] == "prompt-versioning-mcp"
        assert "capabilities" in result["result"]

    def test_ping_request(self, mcp_server):
        """Test ping request handling."""
        request_data = {"jsonrpc": "2.0", "id": 2, "method": "ping", "params": {}}

        response = mcp_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert result["jsonrpc"] == "2.0"
        assert result["id"] == 2
        assert result["result"] == {}

    def test_invalid_json(self, mcp_server):
        """Test handling of invalid JSON."""
        response = mcp_server.handle_request("invalid json {")
        result = json.loads(response)

        assert result["jsonrpc"] == "2.0"
        assert result["id"] is None
        assert "error" in result
        assert result["error"]["code"] == -32700  # Parse error

    def test_invalid_method(self, mcp_server):
        """Test handling of unknown method."""
        request_data = {"jsonrpc": "2.0", "id": 3, "method": "unknown_method", "params": {}}

        response = mcp_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert result["jsonrpc"] == "2.0"
        assert result["id"] == 3
        assert "error" in result
        assert result["error"]["code"] == -32601  # Method not found

    def test_missing_required_field(self, mcp_server):
        """Test handling of request missing required fields."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 4,
            # Missing "method" field
        }

        response = mcp_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert result["jsonrpc"] == "2.0"
        assert result["id"] == 4
        assert "error" in result
        assert result["error"]["code"] == -32600  # Invalid request


# ============================================================================
# Tool Handler Tests
# ============================================================================


class TestToolHandlers:
    """Test all MCP tool handlers."""

    def test_tools_list(self, mcp_server):
        """Test listing available tools."""
        request_data = {"jsonrpc": "2.0", "id": 10, "method": "tools/list", "params": {}}

        response = mcp_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert result["id"] == 10
        assert "result" in result
        assert "tools" in result["result"]

        tools = result["result"]["tools"]
        tool_names = [tool["name"] for tool in tools]

        # Verify all 10 tools are present
        expected_tools = [
            "promptvc_init_repository",
            "promptvc_commit",
            "promptvc_get_history",
            "promptvc_diff",
            "promptvc_checkout",
            "promptvc_tag",
            "promptvc_list_tags",
            "promptvc_get_status",
            "promptvc_generate_audit",
            "promptvc_rollback",
        ]

        for tool_name in expected_tools:
            assert tool_name in tool_names

    def test_init_repository_tool(self, mcp_server):
        """Test init_repository tool."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "tools/call",
            "params": {"name": "promptvc_init_repository", "arguments": {}},
        }

        response = mcp_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert result["id"] == 11
        assert "result" in result
        assert result["result"]["success"] is True
        assert "Repository initialized" in result["result"]["message"]

    def test_commit_tool(self, initialized_server):
        """Test commit tool."""
        # Create a test prompt file with valid Prompt model fields
        prompt_path = initialized_server.repo_path / "test_prompt.yaml"
        prompt_path.write_text("system: You are a helpful assistant\nuser_template: Hello world")

        request_data = {
            "jsonrpc": "2.0",
            "id": 12,
            "method": "tools/call",
            "params": {
                "name": "promptvc_commit",
                "arguments": {"file": "test_prompt.yaml", "message": "Initial commit"},
            },
        }

        response = initialized_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert result["id"] == 12
        assert "result" in result
        assert result["result"]["success"] is True
        assert "hash" in result["result"]
        assert len(result["result"]["hash"]) == 16  # Shortened hash

    def test_get_history_tool(self, initialized_server):
        """Test get_history tool."""
        # Create and commit a prompt using MCP handler
        prompt_path = initialized_server.repo_path / "test_prompt.yaml"
        prompt_path.write_text("system: Hello world")

        # Use MCP handler to commit (which supports file parameter)
        commit_request = {
            "jsonrpc": "2.0",
            "id": 99,
            "method": "tools/call",
            "params": {
                "name": "promptvc_commit",
                "arguments": {"file": "test_prompt.yaml", "message": "Initial commit"},
            },
        }
        initialized_server.handle_request(json.dumps(commit_request))

        request_data = {
            "jsonrpc": "2.0",
            "id": 13,
            "method": "tools/call",
            "params": {"name": "promptvc_get_history", "arguments": {}},
        }

        response = initialized_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert result["id"] == 13
        assert "result" in result
        assert "commits" in result["result"]
        assert len(result["result"]["commits"]) == 1
        assert result["result"]["commits"][0]["message"] == "Initial commit"

    def test_diff_tool(self, initialized_server):
        """Test diff tool."""
        # Create and commit two versions
        prompt_path = initialized_server.repo_path / "test_prompt.yaml"

        prompt_path.write_text("system: Hello world v1")
        repo = PromptRepository(initialized_server.repo_path)
        import yaml
        with open(prompt_path) as f:
            prompt_data = yaml.safe_load(f)
        commit1 = repo.commit(message="Version 1", prompt_data=prompt_data, author="system")
        hash1 = commit1.hash

        prompt_path.write_text("system: Hello world v2")
        import yaml
        with open(prompt_path) as f:
            prompt_data = yaml.safe_load(f)
        commit2 = repo.commit(message="Version 2", prompt_data=prompt_data, author="system")
        hash2 = commit2.hash

        request_data = {
            "jsonrpc": "2.0",
            "id": 14,
            "method": "tools/call",
            "params": {
                "name": "promptvc_diff",
                "arguments": {"version1": hash1, "version2": hash2},
            },
        }

        response = initialized_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert result["id"] == 14
        assert "result" in result
        assert "diff_text" in result["result"]
        assert "v1" in result["result"]["diff_text"]
        assert "v2" in result["result"]["diff_text"]

    def test_checkout_tool(self, initialized_server):
        """Test checkout tool."""
        # Create and commit a prompt
        prompt_path = initialized_server.repo_path / "test_prompt.yaml"
        prompt_path.write_text("system: Hello world v1")

        repo = PromptRepository(initialized_server.repo_path)
        import yaml
        with open(prompt_path) as f:
            prompt_data = yaml.safe_load(f)
        commit1 = repo.commit(message="Version 1", prompt_data=prompt_data, author="system")
        hash1 = commit1.hash

        # Make another commit
        prompt_path.write_text("system: Hello world v2")
        import yaml




        # Checkout first version
        request_data = {
            "jsonrpc": "2.0",
            "id": 15,
            "method": "tools/call",
            "params": {
                "name": "promptvc_checkout",
                "arguments": {"version": hash1},
            },
        }

        response = initialized_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert result["id"] == 15
        assert "result" in result
        assert result["result"]["success"] is True

        # Verify checkout worked by checking the returned prompt
        assert "v1" in result["result"]["prompt"]["system"]

    def test_tag_tool(self, initialized_server):
        """Test tag tool."""
        # Create and commit a prompt
        prompt_path = initialized_server.repo_path / "test_prompt.yaml"
        prompt_path.write_text("system: Hello world")

        repo = PromptRepository(initialized_server.repo_path)
        import yaml
        with open(prompt_path) as f:
            prompt_data = yaml.safe_load(f)
        commit = repo.commit(message="Initial commit", prompt_data=prompt_data, author="system")
        commit_hash = commit.hash

        request_data = {
            "jsonrpc": "2.0",
            "id": 16,
            "method": "tools/call",
            "params": {
                "name": "promptvc_tag",
                "arguments": {
                    "name": "production-v1.0",
                    "hash": commit_hash,
                    "metadata": {"environment": "production", "model": "gpt-4"},
                },
            },
        }

        response = initialized_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert result["id"] == 16
        assert "result" in result
        assert result["result"]["success"] is True

    def test_list_tags_tool(self, initialized_server):
        """Test list_tags tool."""
        # Create a tag
        prompt_path = initialized_server.repo_path / "test_prompt.yaml"
        prompt_path.write_text("system: Hello world")

        repo = PromptRepository(initialized_server.repo_path)
        import yaml
        with open(prompt_path) as f:
            prompt_data = yaml.safe_load(f)
        commit = repo.commit(message="Initial commit", prompt_data=prompt_data, author="system")
        commit_hash = commit.hash
        repo.tag("production-v1.0", commit_hash)

        request_data = {
            "jsonrpc": "2.0",
            "id": 17,
            "method": "tools/call",
            "params": {"name": "promptvc_list_tags", "arguments": {}},
        }

        response = initialized_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert result["id"] == 17
        assert "result" in result
        assert "tags" in result["result"]
        assert len(result["result"]["tags"]) == 1
        assert result["result"]["tags"][0]["name"] == "production-v1.0"

    def test_get_status_tool(self, initialized_server):
        """Test get_status tool."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 18,
            "method": "tools/call",
            "params": {"name": "promptvc_get_status", "arguments": {}},
        }

        response = initialized_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert result["id"] == 18
        assert "result" in result
        assert "initialized" in result["result"]
        assert result["result"]["initialized"] is True

    def test_generate_audit_tool(self, initialized_server):
        """Test generate_audit tool."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 19,
            "method": "tools/call",
            "params": {"name": "promptvc_generate_audit", "arguments": {}},
        }

        response = initialized_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert result["id"] == 19
        assert "result" in result
        assert "data" in result["result"]
        assert result["result"]["success"] is True

    def test_rollback_tool(self, initialized_server):
        """Test rollback tool."""
        # Create and commit two versions
        prompt_path = initialized_server.repo_path / "test_prompt.yaml"

        prompt_path.write_text("system: Hello world v1")
        repo = PromptRepository(initialized_server.repo_path)
        import yaml

        with open(prompt_path) as f:

            prompt_data = yaml.safe_load(f)

        commit1 = repo.commit(message="Version 1", prompt_data=prompt_data, author="system")
        hash1 = commit1.hash

        prompt_path.write_text("system: Hello world v2")
        import yaml

        with open(prompt_path) as f:

            prompt_data = yaml.safe_load(f)

        repo.commit(message="Version 2", prompt_data=prompt_data, author="system")

        # Rollback to first version
        request_data = {
            "jsonrpc": "2.0",
            "id": 20,
            "method": "tools/call",
            "params": {
                "name": "promptvc_rollback",
                "arguments": {"version": hash1},
            },
        }

        response = initialized_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert result["id"] == 20
        assert "result" in result
        assert result["result"]["success"] is True
        # Verify rollback by checking the returned prompt
        assert "v1" in result["result"]["prompt"]["system"]


# ============================================================================
# Resource Handler Tests
# ============================================================================


class TestResourceHandlers:
    """Test MCP resource handlers."""

    def test_resources_list(self, initialized_server):
        """Test listing available resources."""
        request_data = {"jsonrpc": "2.0", "id": 30, "method": "resources/list", "params": {}}

        response = initialized_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert result["id"] == 30
        assert "result" in result
        assert "resources" in result["result"]

        resources = result["result"]["resources"]
        resource_uris = [r["uri"] for r in resources]

        assert "promptvc://status" in resource_uris
        assert "promptvc://history" in resource_uris
        assert "promptvc://tags" in resource_uris

    def test_read_status_resource(self, initialized_server):
        """Test reading status resource."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 31,
            "method": "resources/read",
            "params": {"uri": "promptvc://status"},
        }

        response = initialized_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert result["id"] == 31
        assert "result" in result
        assert "contents" in result["result"]

    def test_read_history_resource(self, initialized_server):
        """Test reading history resource."""
        # Create a commit first
        prompt_path = initialized_server.repo_path / "test_prompt.yaml"
        prompt_path.write_text("system: Hello world")

        repo = PromptRepository(initialized_server.repo_path)
        import yaml

        with open(prompt_path) as f:

            prompt_data = yaml.safe_load(f)

        repo.commit(message="Initial commit", prompt_data=prompt_data, author="system")

        request_data = {
            "jsonrpc": "2.0",
            "id": 32,
            "method": "resources/read",
            "params": {"uri": "promptvc://history"},
        }

        response = initialized_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert result["id"] == 32
        assert "result" in result
        assert "contents" in result["result"]

    def test_read_tags_resource(self, initialized_server):
        """Test reading tags resource."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 33,
            "method": "resources/read",
            "params": {"uri": "promptvc://tags"},
        }

        response = initialized_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert result["id"] == 33
        assert "result" in result
        assert "contents" in result["result"]

    def test_read_unknown_resource(self, initialized_server):
        """Test reading unknown resource."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 34,
            "method": "resources/read",
            "params": {"uri": "promptvc://unknown"},
        }

        response = initialized_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert result["id"] == 34
        assert "error" in result
        assert result["error"]["code"] == -32602  # Invalid params


# ============================================================================
# Authentication Tests
# ============================================================================


class TestAuthentication:
    """Test authentication and authorization."""

    def test_unauthenticated_server_allows_all(self, mcp_server):
        """Test that server without auth token allows all requests."""
        request_data = {"jsonrpc": "2.0", "id": 40, "method": "tools/list", "params": {}}

        response = mcp_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert "result" in result
        assert "error" not in result

    def test_authenticated_server_requires_token(self, authenticated_server):
        """Test that server with auth token requires authentication."""
        request_data = {"jsonrpc": "2.0", "id": 41, "method": "tools/list", "params": {}}

        response = authenticated_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert "error" in result
        assert result["error"]["code"] == -32001  # Unauthorized

    def test_valid_token_allows_access(self, authenticated_server):
        """Test that valid token grants access."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 42,
            "method": "tools/list",
            "params": {"token": "test-token-12345"},
        }

        response = authenticated_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert "result" in result
        assert "error" not in result

    def test_invalid_token_denies_access(self, authenticated_server):
        """Test that invalid token denies access."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 43,
            "method": "tools/list",
            "params": {"token": "wrong-token"},
        }

        response = authenticated_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert "error" in result
        assert result["error"]["code"] == -32001  # Unauthorized


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_tool_call_missing_arguments(self, mcp_server):
        """Test tool call with missing required arguments."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 50,
            "method": "tools/call",
            "params": {
                "name": "promptvc_commit"
                # Missing "arguments" field
            },
        }

        response = mcp_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        # Missing arguments gets passed to handler which returns error in result
        assert "result" in result
        assert result["result"]["success"] is False
        assert "error" in result["result"]

    def test_tool_call_unknown_tool(self, mcp_server):
        """Test calling unknown tool."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 51,
            "method": "tools/call",
            "params": {"name": "promptvc_unknown_tool", "arguments": {}},
        }

        response = mcp_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        assert "error" in result
        assert result["error"]["code"] == -32602  # Invalid params

    def test_commit_nonexistent_file(self, initialized_server):
        """Test committing nonexistent file."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 52,
            "method": "tools/call",
            "params": {
                "name": "promptvc_commit",
                "arguments": {"file": "nonexistent.yaml", "message": "Test"},
            },
        }

        response = initialized_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        # Handler returns error in result, not top-level error
        assert "result" in result
        assert result["result"]["success"] is False
        assert "error" in result["result"]

    def test_diff_invalid_hash(self, initialized_server):
        """Test diff with invalid hash."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 53,
            "method": "tools/call",
            "params": {
                "name": "promptvc_diff",
                "arguments": {
                    "file": "test.yaml",
                    "hash1": "invalid-hash",
                    "hash2": "invalid-hash",
                },
            },
        }

        response = initialized_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        # Handler returns error in result for invalid hashes
        assert "result" in result
        assert result["result"]["success"] is False
        assert "error" in result["result"]

    def test_checkout_invalid_hash(self, initialized_server):
        """Test checkout with invalid hash."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 54,
            "method": "tools/call",
            "params": {
                "name": "promptvc_checkout",
                "arguments": {"file": "test.yaml", "hash": "invalid-hash"},
            },
        }

        response = initialized_server.handle_request(json.dumps(request_data))
        result = json.loads(response)

        # Handler returns error in result for invalid hashes
        assert "result" in result
        assert result["result"]["success"] is False
        assert "error" in result["result"]


# ============================================================================
# Integration Tests
# ============================================================================


class TestMCPIntegration:
    """Test end-to-end MCP workflows."""

    def test_complete_workflow(self, mcp_server):
        """Test complete workflow: init -> commit -> tag -> history."""
        # Step 1: Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 100,
            "method": "tools/call",
            "params": {"name": "promptvc_init_repository", "arguments": {}},
        }
        response = mcp_server.handle_request(json.dumps(init_request))
        assert "result" in json.loads(response)

        # Step 2: Create and commit file
        prompt_path = mcp_server.repo_path / "workflow_test.yaml"
        prompt_path.write_text("system: Workflow test")

        commit_request = {
            "jsonrpc": "2.0",
            "id": 101,
            "method": "tools/call",
            "params": {
                "name": "promptvc_commit",
                "arguments": {"file": "workflow_test.yaml", "message": "Initial workflow commit"},
            },
        }
        response = mcp_server.handle_request(json.dumps(commit_request))
        result = json.loads(response)
        assert "result" in result
        commit_hash = result["result"]["hash"]

        # Step 3: Tag the commit
        tag_request = {
            "jsonrpc": "2.0",
            "id": 102,
            "method": "tools/call",
            "params": {
                "name": "promptvc_tag",
                "arguments": {"name": "workflow-v1", "hash": commit_hash},
            },
        }
        response = mcp_server.handle_request(json.dumps(tag_request))
        assert "result" in json.loads(response)

        # Step 4: Get history
        history_request = {
            "jsonrpc": "2.0",
            "id": 103,
            "method": "tools/call",
            "params": {"name": "promptvc_get_history", "arguments": {"file": "workflow_test.yaml"}},
        }
        response = mcp_server.handle_request(json.dumps(history_request))
        result = json.loads(response)

        assert "result" in result
        assert len(result["result"]["commits"]) == 1
        assert result["result"]["commits"][0]["message"] == "Initial workflow commit"

    def test_version_control_workflow(self, initialized_server):
        """Test version control workflow: commit -> modify -> commit -> diff -> rollback."""
        prompt_path = initialized_server.repo_path / "version_test.yaml"

        # Version 1
        prompt_path.write_text("system: Version 1")
        commit1_request = {
            "jsonrpc": "2.0",
            "id": 110,
            "method": "tools/call",
            "params": {
                "name": "promptvc_commit",
                "arguments": {"file": "version_test.yaml", "message": "Version 1"},
            },
        }
        response = initialized_server.handle_request(json.dumps(commit1_request))
        result = json.loads(response)
        hash1 = result["result"]["hash"]

        # Version 2
        prompt_path.write_text("system: Version 2")
        commit2_request = {
            "jsonrpc": "2.0",
            "id": 111,
            "method": "tools/call",
            "params": {
                "name": "promptvc_commit",
                "arguments": {"file": "version_test.yaml", "message": "Version 2"},
            },
        }
        response = initialized_server.handle_request(json.dumps(commit2_request))
        result = json.loads(response)
        hash2 = result["result"]["hash"]

        # Diff
        diff_request = {
            "jsonrpc": "2.0",
            "id": 112,
            "method": "tools/call",
            "params": {
                "name": "promptvc_diff",
                "arguments": {"version1": hash1, "version2": hash2},
            },
        }
        response = initialized_server.handle_request(json.dumps(diff_request))
        result = json.loads(response)
        assert "Version 1" in result["result"]["diff_text"]
        assert "Version 2" in result["result"]["diff_text"]

        # Rollback
        rollback_request = {
            "jsonrpc": "2.0",
            "id": 113,
            "method": "tools/call",
            "params": {
                "name": "promptvc_rollback",
                "arguments": {"version": hash1},
            },
        }
        response = initialized_server.handle_request(json.dumps(rollback_request))
        result = json.loads(response)
        assert result["result"]["success"] is True

        # Verify rollback by checking the returned prompt data
        assert "Version 1" in result["result"]["prompt"]["system"]


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

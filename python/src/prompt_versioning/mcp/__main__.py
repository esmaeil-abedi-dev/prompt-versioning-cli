"""
MCP server entry point for running with `python -m prompt_versioning.mcp`.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from .protocol.server import main

if __name__ == "__main__":
    main()

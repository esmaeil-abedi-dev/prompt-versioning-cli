"""
Test suite for Prompt Versioning CLI.

Modular test organization exactly matching source code structure:

tests/
├── test_agent/                    # Mirrors: src/prompt_versioning/agent/
│   ├── test_agent.py              # Tests agent.py
│   ├── test_models.py             # Tests models.py
│   ├── test_conversation.py       # Tests conversation functionality
│   └── test_backends/             # Mirrors: agent/backends/
│       ├── test_base.py           # Tests base.py + mock backend
│       ├── test_openai_backend.py # Tests openai_backend.py
│       ├── test_anthropic_backend.py # Tests anthropic_backend.py
│       └── test_ollama_backend.py # Tests ollama_backend.py
│
├── test_core/                     # Mirrors: src/prompt_versioning/core/
│   ├── test_models.py             # Tests models.py
│   ├── test_repository/           # Mirrors: core/repository/
│   │   └── test_base.py           # Tests base.py + repository operations
│   └── test_storage/              # Mirrors: core/storage/
│       └── (storage tests)
│
├── test_mcp/                      # Mirrors: src/prompt_versioning/mcp/
│   ├── test_protocol/             # Mirrors: mcp/protocol/
│   │   └── test_server.py         # Tests server.py
│   └── test_handlers/             # Mirrors: mcp/handlers/
│       └── (handler tests)
│
├── test_cli/                      # Mirrors: src/prompt_versioning/cli/
│   ├── test_commands/             # Mirrors: cli/commands/
│   │   └── test_basic_commands.py # Tests command execution
│   ├── test_core/                 # Mirrors: cli/core/
│   └── test_utils/                # Mirrors: cli/utils/
│
├── test_utils/                    # Mirrors: src/prompt_versioning/utils/
│   └── test_diff.py               # Tests diff.py
│
└── test_integration.py            # End-to-end integration tests

Total: 27 files across 14 directories
Structure: Exactly mirrors src/prompt_versioning/
Easy expansion: Add test file next to corresponding source file

Run tests by module:
    pytest tests/test_agent/           # All agent tests
    pytest tests/test_agent/test_backends/  # Just backend tests
    pytest tests/test_core/            # All core tests
    pytest tests/test_mcp/             # All MCP tests
    pytest tests/test_cli/             # All CLI tests

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

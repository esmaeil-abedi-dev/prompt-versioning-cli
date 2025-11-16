# Prompt Versioning CLI - Developer Guide

Guide for developers contributing to or extending the Prompt Versioning CLI.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Development Setup](#development-setup)
- [Architecture](#architecture)
- [Testing](#testing)
- [Contributing](#contributing)
- [Publishing](#publishing)

---

## Project Structure

### 🎯 Highly Modular Architecture (65 files, 4,130+ lines)

```
prompt-versioning-cli/
├── python/                          # Python implementation
│   ├── src/prompt_versioning/
│   │   ├── __init__.py             # Package exports
│   │   │
│   │   ├── agent/                   # LLM Agent Module (8 files, 605 lines)
│   │   │   ├── agent.py            # Main agent orchestrator
│   │   │   ├── models.py           # Agent data classes
│   │   │   └── backends/           # LLM backend implementations
│   │   │       ├── base.py         # Abstract backend
│   │   │       ├── openai_backend.py
│   │   │       ├── anthropic_backend.py
│   │   │       └── ollama_backend.py
│   │   │
│   │   ├── mcp/                     # MCP Protocol Module (17 files, 1,038 lines)
│   │   │   ├── protocol/           # Core MCP protocol
│   │   │   │   ├── server.py       # Main server (337 lines)
│   │   │   │   ├── tools.py        # Tool schemas
│   │   │   │   ├── models.py       # Protocol models
│   │   │   │   └── resources.py    # Resource definitions
│   │   │   └── handlers/           # Tool handlers (10 files)
│   │   │       ├── init_repository.py
│   │   │       ├── commit_prompt.py
│   │   │       ├── get_history.py
│   │   │       ├── diff_versions.py
│   │   │       ├── checkout_version.py
│   │   │       ├── tag_experiment.py
│   │   │       ├── list_tags.py
│   │   │       ├── get_status.py
│   │   │       ├── generate_audit.py
│   │   │       └── rollback.py
│   │   │
│   │   ├── core/                    # Core Version Control (16 files, 1,158 lines)
│   │   │   ├── models.py           # Data models (Prompt, Commit, etc.)
│   │   │   ├── repository/         # Repository operations (7 files)
│   │   │   │   ├── base.py         # Main orchestrator
│   │   │   │   ├── commit_ops.py   # Commit operations
│   │   │   │   ├── version_ops.py  # Diff & checkout
│   │   │   │   ├── tag_ops.py      # Tag management
│   │   │   │   ├── audit_ops.py    # Audit logging
│   │   │   │   └── ref_resolver.py # Reference resolution
│   │   │   └── storage/            # Storage backend (7 files)
│   │   │       ├── backend.py      # Main orchestrator
│   │   │       ├── filesystem.py   # File system operations
│   │   │       ├── commit_storage.py
│   │   │       ├── prompt_storage.py
│   │   │       ├── tag_storage.py
│   │   │       └── audit_log.py
│   │   │
│   │   ├── utils/                   # Utilities Module (2 files, 320 lines)
│   │   │   └── diff.py             # Semantic diffing engine
│   │   │
│   │   └── cli/                     # CLI Module (20 files, 822 lines)
│   │       ├── main.py             # CLI orchestrator
│   │       ├── commands/           # Command modules (11 files)
│   │       │   ├── init.py         # Initialize repository
│   │       │   ├── commit.py       # Create commits
│   │       │   ├── log.py          # Show history
│   │       │   ├── diff.py         # Compare versions
│   │       │   ├── checkout.py     # Checkout commits
│   │       │   ├── tag.py          # Create tags
│   │       │   ├── tags.py         # List tags
│   │       │   ├── status.py       # Repository status
│   │       │   ├── audit.py        # Generate audit logs
│   │       │   ├── agent.py        # LLM agent interface
│   │       │   └── mcp.py          # MCP server
│   │       ├── core/               # Repository context
│   │       │   └── repository.py
│   │       └── utils/              # CLI utilities
│   │           ├── output.py       # Formatters
│   │           ├── validation.py   # Input validation
│   │           └── execution.py    # Command execution
│   │
│   ├── tests/                       # Python tests (mirrors src/ structure)
│   │   ├── test_core/
│   │   │   ├── test_models.py
│   │   │   ├── test_repository/
│   │   │   └── test_storage/
│   │   ├── test_agent/
│   │   │   ├── test_agent.py
│   │   │   ├── test_models.py
│   │   │   ├── test_conversation.py
│   │   │   └── test_backends/
│   │   ├── test_mcp/
│   │   │   ├── test_protocol/
│   │   │   └── test_handlers/
│   │   ├── test_cli/
│   │   │   ├── test_commands/
│   │   │   ├── test_core/
│   │   │   └── test_utils/
│   │   ├── test_utils/
│   │   │   └── test_diff.py
│   │   └── test_integration.py
│   └── pyproject.toml               # Python package config
│
├── typescript/                      # TypeScript bindings
│   ├── src/
│   │   ├── index.ts                 # Main exports
│   │   ├── cli.ts                   # CLI wrapper
│   │   └── bindings.ts              # IPC bindings
│   ├── package.json
│   └── tsconfig.json
│
├── docs/                            # Documentation
│   ├── USER_GUIDE.md                # User documentation
│   └── DEVELOPER_GUIDE.md           # This file
│
├── examples/                        # Example prompts
│   └── support-bot-example.md
├── README.md                        # Project overview
├── CONTRIBUTING.md                  # Contribution guide
├── CHANGELOG.md                     # Version history
├── CODE_OF_CONDUCT.md               # Community standards
├── SECURITY.md                      # Security policy
└── LICENSE                          # MIT License
```

### 📊 Module Statistics

| Module | Files | Lines | Avg/File | Purpose |
|--------|-------|-------|----------|---------|
| **Agent** | 8 | 605 | 76 | LLM integration with multiple backends |
| **MCP** | 17 | 1,038 | 61 | Model Context Protocol server |
| **Core** | 16 | 1,158 | 72 | Version control operations |
| **Utils** | 2 | 320 | 160 | Semantic diffing |
| **CLI** | 21 | 978 | 47 | Command-line interface |
| **Total** | **65** | **4,130+** | **63** | Complete project |

### Key Design Principles

1. **Single Responsibility**: Each file has ONE clear purpose
2. **Modular Architecture**: Easy to extend without modifying existing code
3. **No Large Files**: Largest file is 337 lines (was 815 before refactoring)
4. **Clear Separation**: Commands, core logic, storage, and utilities are isolated

### Adding New Features

#### Adding a New CLI Command

Create `cli/commands/mycommand.py`:
```python
import click
from ..core import get_repository
from ..utils import success, error

@click.command()
@click.option("--option", help="Command option")
def mycommand(option: str):
    """Command description."""
    repo = get_repository()
    # Implementation
    success("Done!")
```

Register in `cli/commands/__init__.py` and `cli/main.py`.

#### Adding a New LLM Backend

Create `agent/backends/mybackend.py`:
```python
from .base import LLMBackend

class MyBackend(LLMBackend):
    def generate(self, prompt: str, **kwargs) -> str:
        # Implementation
        pass
```

#### Adding a New MCP Tool

Create `mcp/handlers/mytool.py`:
```python
async def handle_mytool(arguments: Dict[str, Any]) -> List[TextContent]:
    # Implementation
    return [TextContent(type="text", text="Result")]
```

Register in `mcp/protocol/tools.py` and `mcp/protocol/server.py`.

### TypeScript Package

- `index.ts`: Main exports and types
- `cli.ts`: CLI wrapper for Node.js
- `bindings.ts`: IPC bridge to Python backend

---

## Development Setup

### Prerequisites

- Python 3.9+
- Node.js 18+
- Git

### Initial Setup

```bash
# Clone repository
git clone https://github.com/yourusername/prompt-versioning-cli.git
cd prompt-versioning-cli

# Python setup
cd python
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev,agent]"

# TypeScript setup
cd ../typescript
npm install

# Run tests
cd ../python
pytest

cd ../typescript
npm test
```

### Development Workflow

```bash
# Make changes to Python code
cd python/src/prompt_versioning

# Run tests
pytest tests/

# Format code
black src/ tests/
ruff check src/ tests/

# Type checking
mypy src/

# Run CLI locally
python -m prompt_versioning.cli --help
```

---

## Architecture

### Core Repository Design

The repository uses **content-addressable storage** similar to Git:

```
.promptvc/
├── objects/                 # Content-addressable storage
│   ├── ab/
│   │   └── c123...def       # Object file (SHA-256 hash)
│   └── de/
│       └── f456...789
├── refs/
│   └── commits.json         # Commit metadata
├── tags/
│   └── tags.json            # Experiment tags
└── config.json              # Repository config
```

**Content Addressing:**
1. Serialize prompt → YAML
2. Compute SHA-256 hash → `abc123...`
3. Store at `.promptvc/objects/ab/c123...`
4. Record commit in `refs/commits.json`

### Class Hierarchy

```
PromptRepository
├── __init__(path)
├── commit(file, message)
├── get_history(file, limit)
├── diff(file, hash1, hash2)
├── checkout(file, hash)
├── tag(name, hash, metadata)
├── list_tags()
├── get_status()
└── generate_audit()

Prompt (Pydantic Model)
├── system: str
├── user_template: str
├── temperature: float
├── max_tokens: int
└── metadata: dict

Commit (Pydantic Model)
├── hash: str
├── file: str
├── message: str
├── timestamp: datetime
└── parent: Optional[str]
```

### LLM Agent Architecture

```
PromptVCAgent
├── LLMBackend (abstract)
│   ├── OpenAIBackend
│   ├── AnthropicBackend
│   └── OllamaBackend
├── process_message(text) → AgentResponse
├── _extract_command(text) → Optional[str]
└── _execute_command(command) → str
```

**Agent Flow:**
1. User input → `process_message()`
2. LLM generates response + optional command
3. Extract command using regex
4. Execute command via subprocess
5. Return result to user

### MCP Server Architecture

```
PromptVCMCPServer
├── Protocol Handlers
│   ├── handle_initialize()
│   ├── handle_ping()
│   ├── handle_tools_list()
│   ├── handle_tools_call()
│   ├── handle_resources_list()
│   └── handle_resources_read()
├── Tool Handlers (10)
│   ├── _tool_init_repository()
│   ├── _tool_commit()
│   ├── _tool_get_history()
│   └── ... (7 more)
└── Transport
    ├── run_stdio()  # Async stdio
    └── run_http()   # Async HTTP
```

**MCP Protocol Flow:**
```
Client → JSON-RPC Request → Server
Server → Parse & Route → Tool Handler
Tool Handler → PromptRepository → Execute
Server → JSON-RPC Response → Client
```

---

## Testing

### Python Tests

```bash
cd python

# Run all tests
pytest

# Run specific test module
pytest tests/test_core/
pytest tests/test_agent/
pytest tests/test_mcp/

# Run specific test file
pytest tests/test_core/test_repository/test_base.py
pytest tests/test_agent/test_backends/test_openai_backend.py

# Run with coverage
pytest --cov=prompt_versioning --cov-report=html

# Run specific test function
pytest tests/test_core/test_repository/test_base.py::TestPromptRepository::test_commit_prompt
```

### Test Structure

Tests mirror the source code structure exactly:

```
src/prompt_versioning/          tests/
├── agent/                      ├── test_agent/
│   ├── agent.py                │   ├── test_agent.py
│   ├── models.py               │   ├── test_models.py
│   └── backends/               │   └── test_backends/
│       ├── base.py             │       ├── test_base.py
│       ├── openai_backend.py   │       ├── test_openai_backend.py
│       ├── anthropic_backend.py│       ├── test_anthropic_backend.py
│       └── ollama_backend.py   │       └── test_ollama_backend.py
├── core/                       ├── test_core/
│   ├── models.py               │   ├── test_models.py
│   ├── repository/             │   ├── test_repository/
│   └── storage/                │   └── test_storage/
└── ...                         └── ...
```

### Writing Tests

```python
# tests/test_core/test_models.py
import pytest
from prompt_versioning.core import PromptRepository

@pytest.fixture
def temp_repo(tmp_path):
    """Create temporary repository for testing."""
    return PromptRepository.init(tmp_path)

def test_commit(temp_repo):
    """Test committing a prompt."""
    # Create prompt file
    prompt_file = temp_repo.path / "test.yaml"
    prompt_file.write_text("system: Test")
    
    # Commit
    commit_hash = temp_repo.commit("test.yaml", "Initial commit")
    
    # Verify
    assert len(commit_hash) == 64  # SHA-256 hash
    assert temp_repo.get_history("test.yaml")
```

### TypeScript Tests

```bash
cd typescript
npm test
```

### Integration Tests

```bash
# Python end-to-end tests
pytest tests/test_integration.py

# Manual CLI testing
./test_cli.sh
```

---

## Contributing

### Code Style

**Python:**
- PEP 8 compliance (enforced by `black` and `ruff`)
- Type hints for all functions
- Docstrings for public APIs

```python
def commit(self, file: str, message: str) -> str:
    """
    Commit a prompt file to version history.
    
    Args:
        file: Path to prompt file
        message: Commit message
        
    Returns:
        SHA-256 hash of the commit
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    ...
```

**TypeScript:**
- ESLint + Prettier
- Explicit types (no `any`)
- JSDoc for public APIs

### Pull Request Process

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes with tests**
   ```bash
   # Add feature
   # Add tests
   pytest
   ```

4. **Format and lint**
   ```bash
   black src/ tests/
   ruff check src/ tests/
   mypy src/
   ```

5. **Commit with conventional commits**
   ```bash
   git commit -m "feat: add support for multi-file commits"
   git commit -m "fix: resolve diff edge case with empty files"
   git commit -m "docs: update USER_GUIDE with new examples"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   # Open pull request on GitHub
   ```

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding tests
- `chore`: Maintenance tasks

**Example:**
```
feat(agent): add Ollama backend for local inference

Implement OllamaBackend class that connects to local Ollama server.
Allows users to run LLM agent without cloud API keys.

Closes #42
```

---

## Publishing

### Python Package

```bash
cd python

# Update version in pyproject.toml
# Update CHANGELOG.md

# Build package
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

### TypeScript Package

```bash
cd typescript

# Update version in package.json
npm version patch  # or minor, major

# Build
npm run build

# Publish
npm publish
```

### Release Checklist

- [ ] Update version numbers (`pyproject.toml`, `package.json`)
- [ ] Update `CHANGELOG.md` with changes
- [ ] Run full test suite (`pytest`, `npm test`)
- [ ] Build packages (`python -m build`, `npm run build`)
- [ ] Test installations locally
- [ ] Create Git tag (`git tag v1.0.0`)
- [ ] Push tag (`git push origin v1.0.0`)
- [ ] Publish to PyPI and npm
- [ ] Create GitHub release with notes

---

## CI/CD with GitHub Actions

### Python Tests

`.github/workflows/python-tests.yml`:

```yaml
name: Python Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          cd python
          pip install -e ".[dev,agent]"
      - name: Run tests
        run: |
          cd python
          pytest --cov
```

### TypeScript Tests

`.github/workflows/typescript-tests.yml`:

```yaml
name: TypeScript Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18
      - name: Install dependencies
        run: |
          cd typescript
          npm install
      - name: Run tests
        run: |
          cd typescript
          npm test
```

---

## Debugging

### Python Debugging

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use modern breakpoint()
breakpoint()
```

### Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

### MCP Server Debugging

```bash
# Enable debug logging
export PROMPTVC_LOG_LEVEL=DEBUG
promptvc mcp-server 2> mcp-debug.log

# Tail logs
tail -f mcp-debug.log
```

---

## Common Development Tasks

### Adding a New CLI Command

1. **Add command in `cli.py`:**
   ```python
   @cli.command()
   @click.option("--option", help="Description")
   def new_command(option: str):
       """Command description."""
       # Implementation
       pass
   ```

2. **Add tests in `tests/test_cli.py`:**
   ```python
   def test_new_command():
       result = runner.invoke(cli, ["new-command", "--option", "value"])
       assert result.exit_code == 0
   ```

3. **Update `docs/USER_GUIDE.md`**

### Adding a New MCP Tool

1. **Define tool in `mcp_server.py`:**
   ```python
   def _tool_new_operation(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
       """Handle new operation."""
       # Implementation
       return {"success": True, "result": "..."}
   ```

2. **Register in `_get_tools()`:**
   ```python
   {
       "name": "promptvc_new_operation",
       "description": "Description",
       "inputSchema": {
           "type": "object",
           "properties": {...},
           "required": [...]
       }
   }
   ```

3. **Add tests in `tests/test_mcp_server.py`**

### Adding a New LLM Backend

1. **Create backend file in `agent/backends/`:**
   ```python
   # src/prompt_versioning/agent/backends/new_backend.py
   from .base import LLMBackend
   
   class NewBackend(LLMBackend):
       def __init__(self, api_key: str, model: str):
           # Initialize client
           
       def generate(self, messages: List[Dict[str, str]]) -> str:
           # Call API
           return response
   ```

2. **Register in `agent/backends/__init__.py`**

3. **Add tests in `tests/test_agent/test_backends/test_new_backend.py`**

---

## Resources

- **Git Internals:** https://git-scm.com/book/en/v2/Git-Internals-Git-Objects
- **Click Documentation:** https://click.palletsprojects.com/
- **Pydantic Documentation:** https://docs.pydantic.dev/
- **MCP Specification:** https://modelcontextprotocol.io/

---

## Getting Help

- **Issues:** https://github.com/yourusername/prompt-versioning-cli/issues
- **Discussions:** https://github.com/yourusername/prompt-versioning-cli/discussions
- **Contributing:** See [CONTRIBUTING.md](../CONTRIBUTING.md)

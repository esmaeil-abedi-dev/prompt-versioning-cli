# 🔄 Prompt Versioning CLI

<div align="center">

![Version Control for Prompts](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![Node.js](https://img.shields.io/badge/node.js-18+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)

**Git-like version control for LLM prompts with lineage tracking, A/B testing, and compliance audit trails.**

[Quick Start](#quick-start) • [User Guide](docs/USER_GUIDE.md) • [Developer Guide](docs/DEVELOPER_GUIDE.md) • [Contributing](CONTRIBUTING.md)

</div>

---

## 🎯 Why Prompt Versioning?

Modern AI applications require systematic prompt management:

- **🔍 Track Changes**: Know exactly what changed between prompt iterations
- **🔄 Easy Rollback**: Instantly revert to previous versions when experiments fail
- **🧪 A/B Testing**: Tag experiments with metadata for performance comparison
- **📊 Compliance**: Generate audit trails for SOC2, GDPR, and regulatory requirements
- **👥 Team Collaboration**: Share prompt history without email chains or Google Docs

## ✨ Features

| Feature | prompt-versioning-cli | Manual Files | Google Docs |
|---------|----------------------|--------------|-------------|
| Commit History | ✅ | ❌ | ⚠️ (limited) |
| Semantic Diff | ✅ | ❌ | ❌ |
| Instant Rollback | ✅ | ⚠️ (manual) | ⚠️ (manual) |
| Experiment Tagging | ✅ | ❌ | ❌ |
| Audit Exports | ✅ (CSV/JSON) | ❌ | ❌ |
| Local-First | ✅ | ✅ | ❌ |
| Git-like UX | ✅ | ❌ | ❌ |
| 🤖 LLM Agent | ✅ | ❌ | ❌ |
| 🔌 MCP Server | ✅ | ❌ | ❌ |

### 🆕 LLM-Powered Conversational Agent

**Talk to your prompt repository in natural language:**

```bash
# Instead of memorizing commands...
promptvc agent "initialize the project"
promptvc agent "show me the last 5 commits"
promptvc agent "what changed between version abc123 and HEAD?"

# Or use interactive mode
promptvc agent --interactive
```

**Features:**
- 🗣️ Natural language commands
- 🧠 Multiple LLM backends (OpenAI, Anthropic, Ollama)
- 🔒 Privacy-first local inference option
- 💬 Multi-turn conversations with context

### 🆕 Model Context Protocol (MCP) Server

**Integrate with VSCode Copilot, Claude Desktop, and other MCP clients:**

```bash
# Easy setup - automatically creates configuration
promptvc mcp-setup --ide vscode    # For VSCode
promptvc mcp-setup --ide claude    # For Claude Desktop
promptvc mcp-setup --ide zed       # For Zed Editor

# Or manually start the server
promptvc mcp-server

# Then ask Copilot:
# "@workspace /prompt-version commit this prompt"
# "@workspace /prompt-version show history"
```

**Features:**
- 🔌 Standardized MCP protocol (JSON-RPC 2.0)
- 🤖 Works with VSCode Copilot, Claude Desktop, Zed
- 🔒 Optional authentication via token
- 📡 Stdio and HTTP transports
- 🛠️ 10 tools: init, commit, history, diff, checkout, tag, status, audit, rollback

## 🚀 Quick Start

### Installation

Choose your preferred language:

#### Python (pip)

```bash
# Install from PyPI
pip install prompt-versioning-cli

# Verify installation
promptvc --version

# Optional: Install with agent features
pip install prompt-versioning-cli[agent]
```

**Requirements:** Python 3.9+

#### TypeScript/Node.js (npm)

```bash
# Install globally
npm install -g prompt-versioning-cli

# Or install locally in your project
npm install prompt-versioning-cli

# Verify installation
promptvc --version
```

**Requirements:** Node.js 18+, npm 9+

> 📚 **New to prompt versioning?** Check out our [Quick Start Guide](docs/QUICKSTART.md) for a step-by-step tutorial!

### 5-Minute Tutorial

```bash
# 1. Initialize a prompt repository
promptvc init
# ✓ Initialized prompt repository in .prompt-vc/

# 2. Create your first prompt interactively
promptvc create-prompt prompts/support-bot.yaml
# 🎨 Creating prompt file interactively...
# System message: You are a friendly customer support agent.
# User template: Help me with: {issue}
# Temperature (0.0-2.0, press Enter to skip): 0.7
# Max tokens (press Enter to skip): 500
# ✓ Prompt file created: prompts/support-bot.yaml

# Or create non-interactively
promptvc create-prompt prompts/quick-prompt.yaml \
  --system "You are helpful" \
  --temperature 0.7

# 3. Commit the prompt
promptvc commit -m "Initial support prompt" -f support-prompt.yaml
# [main a1b2c3d] Initial support prompt

# 4. Make changes and commit again
# Edit support-prompt.yaml to make tone more empathetic...
promptvc commit -m "Made tone more empathetic" -f support-prompt.yaml
# [main e4f5g6h] Made tone more empathetic

# 5. View history
promptvc log
# commit e4f5g6h
# Author: system
# Date: 2025-11-02 10:30:45
# 
#     Made tone more empathetic
# 
# commit a1b2c3d
# Author: system
# Date: 2025-11-02 10:15:22
# 
#     Initial support prompt

# 6. Compare versions
promptvc diff a1b2c3d e4f5g6h
# Shows semantic diff with highlighted changes

# 7. Tag for experiments
promptvc tag experiment-v2 --metadata '{"model":"gpt-4","conversion":0.68}'
# Tagged e4f5g6h as experiment-v2

# 8. Rollback if needed
promptvc checkout a1b2c3d
# Reverted to commit a1b2c3d

# 9. Generate compliance audit
promptvc audit --format csv --output audit.csv
# Exported audit log to audit.csv
```

### 🎨 Creating Prompts Made Easy

No need to manually create YAML files! Use the interactive `create-prompt` command:

```bash
# Interactive mode - step-by-step prompts
promptvc create-prompt
# 🎨 Creating prompt file interactively...
# Prompt file path [prompts/prompt.yaml]: prompts/support-bot.yaml
# System message: You are a warm, empathetic customer support agent.
# User template: Customer: {customer_name}, Issue: {issue}
# Temperature (0.0-2.0, press Enter to skip): 0.7
# Max tokens (press Enter to skip): 800
# ...
# ✓ Prompt file created: prompts/support-bot.yaml

# Quick creation with flags
promptvc create-prompt prompts/quick-bot.yaml \
  --system "You are helpful" \
  --user-template "Question: {question}" \
  --temperature 0.7 \
  --max-tokens 500

# Simple filename (automatically placed in prompts/ directory)
promptvc create-prompt customer-support.yaml \
  --system "You are a customer support agent"
# ✓ Creates: prompts/customer-support.yaml

# Append/update existing file
promptvc create-prompt prompts/support-bot.yaml --append

# Let the agent help you create prompts!
promptvc agent --create-prompt
# 🤖 Agent will ask questions and generate the create-prompt command for you

# Agent can also do it in interactive mode
promptvc agent --interactive
You → I need to create a prompt for a code reviewer
🤖 Assistant: I'll help you create a code review prompt. What programming 
   languages should it focus on?
You → Python and JavaScript
🤖 Assistant: Great! Should it focus on any specific aspects like...
```

## 🛠️ Usage Examples

### Python Library - Core Repository API

```python
from prompt_versioning.core import PromptRepository

# Initialize repository
repo = PromptRepository.init("./my-prompts")

# Commit a prompt
prompt_data = {
    "system": "You are a helpful assistant.",
    "temperature": 0.7
}
commit = repo.commit("Initial prompt", prompt_data)
print(f"Created commit: {commit.hash}")

# View history
for version in repo.log():
    print(f"{version.commit.hash[:7]} - {version.commit.message}")

# Get diff between commits
diff = repo.diff(commit1_hash, commit2_hash)
print(diff.format())

# Tag experiment
tag = repo.tag("experiment-baseline", metadata={"accuracy": 0.85})

# Generate audit log
audit_data = repo.audit_log(format="json")
```

### Python Library - LLM Agent API

```python
from prompt_versioning.agent import PromptVCAgent
from prompt_versioning.agent.backends import OpenAIBackend, OllamaBackend

# Use OpenAI backend
backend = OpenAIBackend(api_key="your-key", model="gpt-4")
agent = PromptVCAgent(backend=backend, repo_path="./my-prompts")

# Natural language commands
response = agent.process_message("show me the last 5 commits")
print(response.message)
if response.command:
    print(f"Command: {response.command}")

# Or use local Ollama (privacy-first)
local_backend = OllamaBackend(model="llama3.2")
local_agent = PromptVCAgent(backend=local_backend, repo_path="./my-prompts")

# Multi-turn conversation
response1 = local_agent.process_message("initialize the repository")
response2 = local_agent.process_message("now show me the status")

# Save conversation history
local_agent.save_conversation("conversation.json")
```

### Python Library - MCP Server API

```python
from prompt_versioning.mcp import PromptVCMCPServer
import asyncio

# Create MCP server
server = PromptVCMCPServer(
    repo_path="./my-prompts",
    auth_token="optional-token"
)

# Start server (stdio transport)
async def main():
    await server.run_stdio()

asyncio.run(main())

# Or start HTTP server
# await server.run_http(host="localhost", port=8080)
```

### TypeScript/Node.js

```typescript
import { PromptRepository } from 'prompt-versioning-cli';

// Initialize repository
const repo = await PromptRepository.init('./my-prompts');

// Commit a prompt
const commit = await repo.commit('Initial prompt', {
  system: 'You are a helpful assistant.',
  temperature: 0.7
});

// View history
const versions = await repo.log();
versions.forEach(v => console.log(`${v.commit.hash.slice(0, 7)} - ${v.commit.message}`));

// Get diff
const diff = await repo.diff(commit1Hash, commit2Hash);
console.log(diff.format());

// Tag experiment
const tag = await repo.tag('experiment-baseline', { accuracy: 0.85 });

// Generate audit log
const audit = await repo.auditLog({ format: 'json' });
```

## 🏗️ Architecture

### Highly Modular Design (65 files, 4,130+ lines)

The project uses a **super modular architecture** with clear separation of concerns:

| Module | Files | Lines | Purpose |
|--------|-------|-------|---------|
| **CLI** | 21 | 978 | Command-line interface (one file per command) |
| **MCP** | 17 | 1,038 | Model Context Protocol server & tools |
| **Core** | 16 | 1,158 | Version control (repository + storage) |
| **Agent** | 8 | 605 | LLM integration (OpenAI/Anthropic/Ollama) |
| **Utils** | 2 | 320 | Semantic diffing engine |
| **Total** | **65** | **4,130+** | Average: **63 lines/file** |

**Key Benefits:**
- ✅ Easy to add new CLI commands (just create one file)
- ✅ Easy to add new LLM backends (just create one file)
- ✅ Easy to add new MCP tools (just create one file)
- ✅ No file over 400 lines (was 815 before refactoring)
- ✅ Perfect for team collaboration

See [Developer Guide](docs/DEVELOPER_GUIDE.md) for detailed architecture documentation.

## 📚 Documentation

- **[User Guide](docs/USER_GUIDE.md)** - Complete guide for using the CLI (installation, commands, LLM agent, MCP server, production usage)
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Architecture, development setup, contributing, testing
- **[Contributing](CONTRIBUTING.md)** - How to contribute to the project
- **[Changelog](CHANGELOG.md)** - Version history and release notes
- **[Security Policy](SECURITY.md)** - Security vulnerabilities and reporting

## 🧪 Running Tests

**Python**
```bash
cd python
pytest tests/ -v --cov=prompt_versioning
```

**TypeScript**
```bash
cd typescript
npm test
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/prompt-versioning-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/prompt-versioning-cli/discussions)

---

<div align="center">

**Built with ❤️ for prompt engineers and ML teams**

⭐ Star us on GitHub if this project helps you!

</div>

# Prompt Versioning CLI - User Guide

Complete guide for using the Prompt Versioning CLI.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Creating Prompts](#creating-prompts)
- [Core Commands](#core-commands)
- [LLM Agent Mode](#llm-agent-mode)
- [MCP Server Integration](#mcp-server-integration)
- [YAML Schema](#yaml-schema)
- [Production Usage](#production-usage)

---

## Installation

### Python

```bash
pip install prompt-versioning-cli

# With LLM agent and MCP server support
pip install prompt-versioning-cli[agent]
```

### Node.js

```bash
npm install -g prompt-versioning-cli
```

---

## Quick Start

```bash
# 1. Initialize repository
promptvc init

# 2. Create a prompt file (support-bot.yaml)
cat > support-bot.yaml << EOF
system: "You are a friendly customer support agent."
user_template: "Help me with: {issue}"
temperature: 0.7
max_tokens: 500
EOF

# 3. Commit the prompt
promptvc commit -m "Initial support prompt" -f support-bot.yaml

# 4. View history
promptvc log

# 5. Make changes and commit again
# Edit support-bot.yaml...
promptvc commit -m "Updated tone" -f support-bot.yaml

# 6. Compare versions (use commit hashes from log)
promptvc diff a1b2c3d e4f5g6h

# 7. Rollback if needed
promptvc checkout a1b2c3d -o support-bot.yaml

# 8. Tag experiments
promptvc tag experiment-v1 --metadata '{"accuracy": 0.85}'

# 9. Check repository status
promptvc status
```

---

## Creating Prompts

### `create-prompt` - Interactive Prompt Creation

No need to manually write YAML files! The `create-prompt` command guides you through creating properly formatted prompt files.

```bash
promptvc create-prompt [OPTIONS]
```

**Interactive Mode (Recommended):**

```bash
promptvc create-prompt

# You'll be prompted for:
# - File path (default: prompts/prompt.yaml)
# - System message
# - User template with {variable} placeholders
# - Temperature, max tokens, top-p (all optional)
# - Stop sequences (optional)
```

**Quick Creation with Flags:**

```bash
# Create with basic settings
promptvc create-prompt --name my-bot \
  --system "You are a helpful assistant" \
  --user-template "Question: {question}" \
  --temperature 0.7

# Full configuration
promptvc create-prompt --file prompts/support.yaml \
  --system "You are a customer support agent" \
  --user-template "Customer: {name}, Issue: {issue}" \
  --temperature 0.8 \
  --max-tokens 1000 \
  --top-p 0.95 \
  --stop-sequences "[END],[DONE]" \
  --non-interactive
```

**Options:**

- `--file FILE` / `-f FILE`: Path to prompt file (default: prompts/<name>.yaml)
- `--name NAME`: Prompt name (for automatic file naming)
- `--non-interactive`: Skip interactive prompts, use only provided options
- `--system TEXT`: System message for the LLM
- `--user-template TEXT`: User template with {variable} placeholders
- `--temperature FLOAT`: Temperature (0.0-2.0)
- `--max-tokens INT`: Maximum tokens to generate
- `--top-p FLOAT`: Top-p sampling (0.0-1.0)
- `--stop-sequences TEXT`: Comma-separated stop sequences
- `--append`: Append to existing file instead of creating new

**Examples:**

```bash
# Interactive - best for first-time users
promptvc create-prompt
🎨 Creating prompt file interactively...
Prompt file path [prompts/prompt.yaml]: prompts/reviewer.yaml
System message: You are a code reviewer
User template: Review this code: {code}
Temperature (0.0-2.0, press Enter to skip): 0.3
...
✓ Prompt file created: prompts/reviewer.yaml

# Quick creation for experienced users
promptvc create-prompt --name translator \
  --system "Translate to {target_language}" \
  --non-interactive

# Update existing file
promptvc create-prompt --file prompts/support.yaml \
  --temperature 0.9 \
  --append

# With agent assistance
promptvc agent --create-prompt
🤖 I'll help you create a prompt. What kind of bot are you building?
You → A summarization bot for long articles
🤖 Great! What should the tone be? Professional, casual, or technical?
You → Professional and concise
🤖 I'll create a prompt for you...
Generated command:
promptvc create-prompt --name summarizer --system "You are a professional summarization assistant..." --temperature 0.5
Execute this command to create the prompt? [Y/n]:
```

---

## Core Commands

### `init` - Initialize Repository

```bash
promptvc init [--path PATH]
```

Initialize a new prompt repository in the current directory or specified path.

**Example:**
```bash
promptvc init
promptvc init --path ./my-prompts
```

### `commit` - Save Changes

```bash
promptvc commit -m "MESSAGE" -f FILE [--author AUTHOR] [--path PATH]
```

Commit a prompt file to version history with a descriptive message.

**Example:**
```bash
promptvc commit -m "Improved customer tone" -f support-bot.yaml
promptvc commit -m "Initial version" -f prompts/chat.yaml --author "john@example.com"
```

### `log` - View History

```bash
promptvc log [--max-count N] [--oneline] [--path PATH]
```

Show commit history in reverse chronological order.

**Options:**
- `--max-count N` / `-n N`: Limit number of commits to show
- `--oneline`: Show condensed one-line output
- `--path PATH`: Repository path (default: current directory)

**Example:**
```bash
promptvc log
promptvc log --max-count 5 --oneline
promptvc log -n 10
```

**Options:**
- `--limit N`: Show only the last N commits (default: 10)

### `diff` - Compare Versions

```bash
promptvc diff COMMIT1 COMMIT2 [--path PATH] [--summary]
```

Show differences between two commits.

**Options:**
- `--path PATH`: Repository path (default: current directory)
- `--summary`: Show only summary, not detailed diff

**Example:**
```bash
promptvc diff abc123 def456
promptvc diff HEAD~1 HEAD --summary
```

### `checkout` - Restore Version

```bash
promptvc checkout COMMIT_REF [--path PATH] [--output FILE]
```

Checkout a specific commit and optionally write the prompt to a file.

**Options:**
- `--path PATH`: Repository path (default: current directory)
- `--output FILE` / `-o FILE`: Write prompt to file

**Example:**
```bash
promptvc checkout abc123
promptvc checkout HEAD~2 -o support-bot.yaml
promptvc checkout experiment-v1 --output restored-prompt.yaml
```

### `tag` - Mark Experiments

```bash
promptvc tag TAG_NAME [--commit COMMIT] [--metadata JSON] [--path PATH]
```

Tag a specific version for experiment tracking.

**Options:**
- `--commit COMMIT`: Commit to tag (default: HEAD)
- `--metadata JSON`: JSON string with experiment metadata
- `--path PATH`: Repository path (default: current directory)

**Examples:**
```bash
# Tag current HEAD
promptvc tag production-v1.0

# Tag specific commit
promptvc tag experiment-baseline --commit abc123

# Tag with metadata
promptvc tag experiment-2024-01 --metadata '{"model": "gpt-4", "accuracy": 0.92}'
```

### `tags` - List Tags

```bash
promptvc tags [--path PATH]
```

List all experiment tags with their metadata, sorted by creation date.

**Example:**
```bash
promptvc tags
```

### `status` - Repository Status

```bash
promptvc status [--path PATH]
```

Show current repository status including HEAD commit, message, author, date, and tags.

**Example:**
```bash
promptvc status
```

### `audit` - Generate Reports

```bash
promptvc audit [--format FORMAT] [--output FILE] [--path PATH]
```

Generate compliance audit log with all repository actions.

**Options:**
- `--format FORMAT`: Output format: `json` (default) or `csv`
- `--output FILE` / `-o FILE`: Write to file instead of stdout
- `--path PATH`: Repository path (default: current directory)

**Examples:**
```bash
# Print to stdout
promptvc audit

# Export to file
promptvc audit --format csv --output audit-2024.csv
promptvc audit -o audit.json
```

**Example:**
```bash
promptvc audit --format csv --output audit-report.csv
```

---

## LLM Agent Mode

Talk to your repository using natural language with AI assistance.

### Setup

Install with agent support:
```bash
pip install prompt-versioning-cli[agent]

# Set API key (choose one)
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
# Or use local Ollama (no API key needed)
```

### Single Query Mode

```bash
promptvc agent "show me the last 5 commits"
promptvc agent "what changed between v1.0 and v1.1?"
promptvc agent "tag the latest commit as production"
```

### Interactive Mode

```bash
promptvc agent --interactive

# Start a conversation
You: initialize the repository
Assistant: Repository initialized successfully!

You: commit support-bot.yaml with message "Initial version"
Assistant: ✓ Committed support-bot.yaml [abc123]

You: show me the history
Assistant: [displays commit history]

You: exit
```

### Backend Selection

```bash
# OpenAI GPT-4 (default)
promptvc agent "your query" --backend openai --model gpt-4

# Anthropic Claude
promptvc agent "your query" --backend anthropic --model claude-3-5-sonnet-20241022

# Local Ollama (privacy-first)
promptvc agent "your query" --backend ollama --model llama2
```

### Save Conversations

```bash
# Save conversation to file
promptvc agent --interactive --save conversation.json

# Load previous conversation
promptvc agent --interactive --load conversation.json
```

---

## MCP Server Integration

Integrate with VSCode Copilot, Claude Desktop, and other MCP-compatible clients.

### Quick Setup (Automated)

Use the automated setup command to generate configuration files:

```bash
# For VSCode
promptvc mcp-setup --ide vscode

# For Claude Desktop
promptvc mcp-setup --ide claude

# For Zed Editor
promptvc mcp-setup --ide zed
```

This automatically:
- ✅ Creates the correct config file in the right location
- ✅ Sets up the repository path
- ✅ Configures authentication (optional)
- ✅ Shows you next steps

Then just restart your IDE and start using MCP tools!

### Manual Setup

If you prefer manual configuration:

#### VSCode Configuration

Create `.vscode/mcp-config.json`:

```json
{
  "mcpServers": {
    "promptvc": {
      "command": "python",
      "args": ["-m", "prompt_versioning.cli", "mcp-server", "--path", "${workspaceFolder}/.promptvc"],
      "env": {
        "PROMPTVC_MCP_TOKEN": "${env:PROMPTVC_MCP_TOKEN}"
      }
    }
  }
}
```

#### Claude Desktop Configuration

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**Linux:** `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "promptvc": {
      "command": "python",
      "args": ["-m", "prompt_versioning.cli", "mcp-server", "--path", "/path/to/.promptvc"]
    }
  }
}
```

#### Zed Configuration

Edit `~/.config/zed/settings.json`:

```json
{
  "context_servers": {
    "promptvc": {
      "command": {
        "path": "python",
        "args": ["-m", "prompt_versioning.cli", "mcp-server", "--path", "/path/to/.promptvc"]
      }
    }
  }
}
```

### Start MCP Server

```bash
# Stdio transport (for local IDEs)
promptvc mcp-server

# HTTP transport (for remote access)
promptvc mcp-server --transport http --port 8080

# With authentication
export PROMPTVC_MCP_TOKEN="your-secure-token"
promptvc mcp-server
```

### VSCode Configuration

Create `.vscode/mcp-config.json`:

```json
{
  "mcpServers": {
    "promptvc": {
      "command": "python",
      "args": ["-m", "prompt_versioning.mcp_server", "--path", "${workspaceFolder}/.promptvc"],
      "env": {
        "PROMPTVC_MCP_TOKEN": "${env:PROMPTVC_MCP_TOKEN}"
      }
    }
  }
}
```

Reload VSCode, then use with Copilot:

```
@workspace /prompt-version commit support-bot.yaml with message "Updated format"
@workspace /prompt-version show me the history
@workspace /prompt-version what changed between v1.0 and v1.1?
```

### Claude Desktop Configuration

**macOS:** Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** Edit `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "promptvc": {
      "command": "python3",
      "args": ["-m", "prompt_versioning.mcp_server", "--path", "/path/to/.promptvc"]
    }
  }
}
```

Restart Claude Desktop and use:
```
Can you commit the current prompt?
Show me the version history
What changed between v1.0 and v1.1?
```

### Available MCP Tools

1. `promptvc_init_repository` - Initialize repository
2. `promptvc_commit` - Commit changes
3. `promptvc_get_history` - Get commit history
4. `promptvc_diff` - Compare versions
5. `promptvc_checkout` - Restore version
6. `promptvc_tag` - Tag experiments
7. `promptvc_list_tags` - List tags
8. `promptvc_get_status` - Repository status
9. `promptvc_generate_audit` - Compliance reports
10. `promptvc_rollback` - Rollback changes

---

## YAML Schema

Prompt files should follow this structure:

### Basic Structure

```yaml
# Required fields
system: "System instruction for the LLM"
user_template: "User prompt template with {variables}"

# Optional fields
temperature: 0.7          # Range: 0.0-1.0
max_tokens: 500          # Max response length
model: "gpt-4"           # Model identifier
```

### Complete Example

```yaml
# Metadata
name: "Customer Support Bot"
version: "1.0"
description: "Friendly support agent for product inquiries"

# LLM Configuration
system: |
  You are a friendly and knowledgeable customer support agent.
  Always be empathetic and provide clear, actionable solutions.
  
  Guidelines:
  - Be polite and professional
  - Ask clarifying questions
  - Provide step-by-step solutions

user_template: |
  Customer Issue: {issue}
  Priority: {priority}
  
  Please provide a helpful response.

# Model Parameters
model: "gpt-4"
temperature: 0.7
max_tokens: 800
top_p: 0.9

# Experiment Metadata
experiment:
  id: "exp-2024-001"
  baseline_accuracy: 0.85
  target_accuracy: 0.90
```

### Variable Interpolation

Use `{variable}` syntax for dynamic content:

```yaml
user_template: |
  Product: {product_name}
  Customer Name: {customer_name}
  Issue: {issue_description}
```

### Multi-Turn Conversations

```yaml
system: "You are a helpful assistant."

conversation:
  - role: user
    content: "What is {topic}?"
  - role: assistant
    content: "Let me explain {topic}..."
  - role: user
    content: "Can you give an example?"

temperature: 0.7
```

---

## Production Usage

### Best Practices

**1. Commit Frequently**
```bash
# After every significant change
promptvc commit -m "Clear, descriptive message" -f prompt.yaml
```

**2. Tag Important Versions**
```bash
# Tag production deployments
promptvc tag production-v1.0 <hash> --metadata '{"deployed": "2024-01-15", "model": "gpt-4"}'

# Tag experiments
promptvc tag experiment-A <hash> --metadata '{"accuracy": 0.92, "latency_ms": 250}'
```

**3. Regular Audits**
```bash
# Generate monthly compliance reports
promptvc audit --format csv --output audit-$(date +%Y-%m).csv
```

**4. Use Version Hashes**
```bash
# Reference specific versions in your code
PROMPT_VERSION="abc123def456"
promptvc checkout -f prompt.yaml $PROMPT_VERSION
```

### Experiment Tracking

Track A/B tests with tags and metadata:

```bash
# Commit baseline
promptvc commit -m "Baseline prompt" -f support-bot.yaml
BASELINE_HASH=$(promptvc log -f support-bot.yaml --limit 1 | grep hash)

# Tag baseline
promptvc tag baseline $BASELINE_HASH --metadata '{
  "model": "gpt-4",
  "temperature": 0.7,
  "accuracy": 0.85,
  "avg_latency_ms": 300
}'

# Test variant A
# Edit support-bot.yaml...
promptvc commit -m "Variant A: More concise responses" -f support-bot.yaml
VARIANT_A_HASH=$(promptvc log -f support-bot.yaml --limit 1 | grep hash)

promptvc tag variant-A $VARIANT_A_HASH --metadata '{
  "model": "gpt-4",
  "temperature": 0.5,
  "accuracy": 0.88,
  "avg_latency_ms": 280
}'

# Compare results
promptvc tags
promptvc diff -f support-bot.yaml $BASELINE_HASH $VARIANT_A_HASH
```

### Compliance & Auditing

Generate audit trails for regulatory compliance:

```bash
# Full audit report (JSON)
promptvc audit --output full-audit.json

# CSV for spreadsheet analysis
promptvc audit --format csv --output audit.csv

# HTML for stakeholder reports
promptvc audit --format html --output audit-report.html
```

**Audit Report Includes:**
- All commits with timestamps and authors
- Version comparisons and changes
- Experiment tags and metadata
- File modification history
- SHA-256 content hashes (tamper-proof)

### Team Collaboration

**1. Shared Repository**
```bash
# Initialize shared repo
promptvc init --path /shared/prompts

# Team members commit changes
promptvc commit -m "Updated by Alice" -f prompt.yaml --path /shared/prompts
```

**2. Review Process**
```bash
# Review recent changes
promptvc log -f prompt.yaml --limit 5

# Compare with previous version
promptvc diff -f prompt.yaml <previous-hash> <current-hash>

# Rollback if needed
promptvc checkout -f prompt.yaml <good-hash>
promptvc commit -m "Reverted to stable version" -f prompt.yaml
```

**3. Production Deployment**
```bash
# Tag for production
promptvc tag production-$(date +%Y%m%d) <hash>

# Deploy using tagged version
PROD_TAG="production-20240115"
promptvc checkout -f prompt.yaml $(promptvc tags | grep $PROD_TAG | awk '{print $2}')
```

### Backup & Recovery

```bash
# Backup repository (copy .promptvc directory)
tar -czf promptvc-backup-$(date +%Y%m%d).tar.gz .promptvc/

# Restore from backup
tar -xzf promptvc-backup-20240115.tar.gz

# Verify integrity
promptvc status
promptvc log -f prompt.yaml
```

### Security

**1. Authentication (MCP Server)**
```bash
# Generate secure token
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Use token
export PROMPTVC_MCP_TOKEN="your-generated-token"
promptvc mcp-server
```

**2. Access Control**
```bash
# Restrict repository access
chmod 700 .promptvc
chmod 600 .promptvc/objects/*
```

**3. Audit Logs**
```bash
# Review all changes
promptvc audit --format json | jq '.commits[] | {timestamp, author, message}'
```

---

## Troubleshooting

### Common Issues

**Problem:** Repository not initialized
```bash
# Solution
promptvc init
```

**Problem:** File not found during commit
```bash
# Solution: Use correct file path
promptvc commit -m "message" -f path/to/prompt.yaml
```

**Problem:** LLM agent not working
```bash
# Solution: Install agent dependencies
pip install prompt-versioning-cli[agent]

# Set API key
export OPENAI_API_KEY="your-key"
```

**Problem:** MCP server not connecting
```bash
# Solution: Check if server is running
ps aux | grep mcp_server

# Restart with debug logging
export PROMPTVC_LOG_LEVEL=DEBUG
promptvc mcp-server 2> mcp-debug.log
```

### Getting Help

- **GitHub Issues:** https://github.com/yourusername/prompt-versioning-cli/issues
- **Discussions:** https://github.com/yourusername/prompt-versioning-cli/discussions
- **Documentation:** https://github.com/yourusername/prompt-versioning-cli/tree/main/docs

---

## Next Steps

- Review [CONTRIBUTING.md](../CONTRIBUTING.md) to contribute to the project
- Check [CHANGELOG.md](../CHANGELOG.md) for version history
- See [examples/](../examples/) for more use cases

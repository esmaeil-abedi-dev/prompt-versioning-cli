# Prompt Versioning CLI - TypeScript/Node.js Package

[![npm version](https://badge.fury.io/js/prompt-versioning-cli.svg)](https://badge.fury.io/js/prompt-versioning-cli)
[![Node.js Version](https://img.shields.io/node/v/prompt-versioning-cli)](https://www.npmjs.com/package/prompt-versioning-cli)
[![License](https://img.shields.io/badge/license-AGPL--3.0-blue.svg)](../LICENSE)

Git-like version control for LLM prompts with TypeScript bindings and CLI.

## 🚀 Installation

### Global Installation (CLI)

```bash
npm install -g prompt-versioning-cli
```

### Local Installation (Library)

```bash
npm install prompt-versioning-cli
```

**Requirements:** Node.js 18+ and npm 9+

## 📦 What's Included

When you install this package, you get:

- **`promptvc` CLI**: Command-line interface (same as Python version)
- **TypeScript/JavaScript API**: Use in your Node.js/TypeScript projects
- **Type definitions**: Full TypeScript support with `.d.ts` files
- **MCP server**: Model Context Protocol server support

## 🎯 Quick Start (CLI)

```bash
# Initialize a prompt repository
promptvc init

# Create a prompt interactively
promptvc create-prompt

# Or create non-interactively
promptvc create-prompt --name my-prompt \
  --system "You are a helpful assistant" \
  --temperature 0.7 \
  --non-interactive

# Commit your prompt
promptvc commit -m "Initial prompt" -f prompts/my-prompt.yaml

# View history
promptvc log
```

## 📖 Documentation

- **[User Guide](../docs/USER_GUIDE.md)** - Complete feature documentation
- **[Developer Guide](../docs/DEVELOPER_GUIDE.md)** - API reference and architecture
- **[Quick Start](../docs/QUICKSTART.md)** - Step-by-step tutorial
- **[Publishing Guide](../docs/PUBLISHING.md)** - How to contribute and publish

## 🔧 Using the TypeScript API

### Initialize Repository

```typescript
import { PromptRepository, Prompt } from 'prompt-versioning-cli';

// Initialize repository
const repo = new PromptRepository('.prompt-vc');
await repo.init();

// Create a prompt
const prompt = new Prompt({
  name: 'my-prompt',
  systemMessage: 'You are a helpful assistant',
  userTemplate: 'Question: {question}',
  temperature: 0.7,
  maxTokens: 500,
});

// Save the prompt
await prompt.save('prompts/my-prompt.yaml');

// Commit the prompt
await repo.commit({
  message: 'Initial prompt',
  files: ['prompts/my-prompt.yaml'],
});
```

### View History

```typescript
// Get commit history
const history = await repo.getHistory();

for (const commit of history) {
  console.log(`${commit.hash.substring(0, 7)}: ${commit.message}`);
  console.log(`  Author: ${commit.author}`);
  console.log(`  Date: ${commit.date}`);
}
```

### Compare Versions

```typescript
// Get diff between commits
const diff = await repo.diff('abc123', 'def456');

console.log('Changes:');
for (const change of diff.changes) {
  console.log(`  ${change.type}: ${change.path}`);
  console.log(`    ${change.description}`);
}
```

### Rollback Changes

```typescript
// Checkout specific commit
await repo.checkout('abc123');

// Or rollback by steps
await repo.rollback({ steps: 2 });
```

### Execute Prompts

```typescript
import { PromptExecutor } from 'prompt-versioning-cli';

// Load and execute a prompt
const executor = new PromptExecutor();
const response = await executor.execute({
  promptFile: 'prompts/my-prompt.yaml',
  variables: {
    question: 'What is version control?',
  },
  model: 'gpt-4',
  apiKey: process.env.OPENAI_API_KEY,
});

console.log(response.content);
```

## 🔌 MCP Server

Use with VSCode Copilot, Claude Desktop, Zed, and other MCP clients:

```bash
# Automatic setup
promptvc mcp-setup --ide vscode
promptvc mcp-setup --ide claude

# Manual start
promptvc mcp-server
```

## 🧪 Development

Clone the repository and set up for development:

```bash
git clone https://github.com/esmaeil-abedi-dev/prompt-versioning-cli.git
cd prompt-versioning-cli/typescript

# Install dependencies
npm install

# Build the project
npm run build

# Run tests
npm test

# Run with watch mode
npm run test:watch

# Lint code
npm run lint

# Format code
npm run format
```

## 📝 Scripts

- `npm run build` - Compile TypeScript to JavaScript
- `npm test` - Run tests with Jest
- `npm run test:watch` - Run tests in watch mode
- `npm run lint` - Lint code with ESLint
- `npm run format` - Format code with Prettier
- `npm run clean` - Remove build artifacts

## 🔗 Type Definitions

This package includes full TypeScript type definitions. Import types:

```typescript
import type {
  Prompt,
  PromptConfig,
  CommitInfo,
  DiffResult,
  Repository,
  ExecuteOptions,
} from 'prompt-versioning-cli';
```

## 📝 License

This project is licensed under the GNU Affero General Public License v3.0 or later (AGPL-3.0-or-later).

See [LICENSE](../LICENSE) for details.

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## 🔗 Links

- **Homepage**: <https://github.com/esmaeil-abedi-dev/prompt-versioning-cli>
- **Documentation**: <https://github.com/esmaeil-abedi-dev/prompt-versioning-cli/tree/main/docs>
- **Issue Tracker**: <https://github.com/esmaeil-abedi-dev/prompt-versioning-cli/issues>
- **npm**: <https://www.npmjs.com/package/prompt-versioning-cli>

## 💬 Support

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and community support
- **Email**: <esmaeilabedi@outlook.com>

import { PromptRepository } from 'prompt-versioning-cli';

// Initialize repository
const repo = await PromptRepository.init('./prompts');

// Commit a prompt
const commit = await repo.commit('Initial prompt', {
  system: 'You are a helpful assistant.',
  temperature: 0.7
});

// View history
const versions = await repo.log();
versions.forEach(v => {
  console.log(`${v.commit.hash.slice(0, 7)} - ${v.commit.message}`);
});

// Compare versions
const diff = await repo.diff(hash1, hash2);
console.log(diff);

// Tag experiments
await repo.tag('experiment-baseline', { accuracy: 0.85 });
```

## Features

- 🔄 **Version Control**: Git-like commit history for prompts
- 📊 **Semantic Diff**: Intelligent comparison of prompt changes
- 🧪 **A/B Testing**: Tag experiments with performance metrics
- 📝 **Audit Trails**: Complete compliance-ready logs
- 🔍 **Rollback**: Instant revert to previous versions
- 🏷️ **Tagging**: Mark important versions and experiments

## API Reference

### PromptRepository

Main class for interacting with prompt repositories.

#### Methods

- `static init(path)`: Initialize a new repository
- `commit(message, promptData, author?)`: Create a commit
- `log(maxCount?)`: Get commit history
- `diff(commit1, commit2)`: Compare two commits
- `checkout(commitRef)`: Checkout a specific commit
- `tag(name, metadata?, commitRef?)`: Create a tag
- `auditLog(format?)`: Generate audit log
- `status()`: Get repository status
- `listTags()`: List all tags

## Development

```bash
# Clone repository
git clone https://github.com/yourusername/prompt-versioning-cli.git
cd prompt-versioning-cli/typescript

# Install dependencies
npm install

# Build
npm run build

# Run tests
npm test

# Lint
npm run lint
```

## License

MIT License - see [LICENSE](../LICENSE) for details.

## Contributing

Contributions welcome! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## Support

- [GitHub Issues](https://github.com/yourusername/prompt-versioning-cli/issues)
- [Documentation](https://github.com/yourusername/prompt-versioning-cli)

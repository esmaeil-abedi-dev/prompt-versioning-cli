# Prompt Versioning CLI - TypeScript/Node.js Package

Git-like version control for LLM prompts with TypeScript bindings.

## Installation

```bash
npm install prompt-versioning-cli
```

**Note:** This package requires the Python CLI to be installed:

```bash
pip install prompt-versioning-cli
```

## Quick Start

### CLI Usage

```bash
# Use the promptvc command (provided by Python package)
promptvc init
promptvc commit -m "Initial prompt" -f prompt.yaml
promptvc log
```

### TypeScript API

```typescript
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

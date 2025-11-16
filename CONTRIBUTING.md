# Contributing to Prompt Versioning CLI

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- **Python**: 3.9 or higher
- **Node.js**: 18 or higher
- **Git**: For version control

### Development Setup

1. **Fork and Clone**

```bash
git clone https://github.com/yourusername/prompt-versioning-cli.git
cd prompt-versioning-cli
```

2. **Set Up Python Environment**

```bash
cd python
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

3. **Set Up TypeScript Environment**

```bash
cd typescript
npm install
```

4. **Run Tests**

```bash
# Python tests
cd python
pytest tests/ -v

# TypeScript tests
cd typescript
npm test
```

## Development Workflow

### Branching Strategy

- `main` - Stable, production-ready code
- `develop` - Integration branch for features
- `feature/xxx` - New features
- `fix/xxx` - Bug fixes
- `docs/xxx` - Documentation updates

### Making Changes

1. **Create a Branch**

```bash
git checkout -b feature/your-feature-name
```

2. **Make Your Changes**

- Write code following style guidelines (see below)
- Add tests for new functionality
- Update documentation

3. **Run Tests and Linters**

```bash
# Python
cd python
pytest tests/
ruff check src/ tests/
black src/ tests/
mypy src/

# TypeScript
cd typescript
npm run lint
npm run build
npm test
```

4. **Commit Your Changes**

```bash
git add .
git commit -m "feat: Add new feature X"
```

Use conventional commit messages:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test updates
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

5. **Push and Create Pull Request**

```bash
git push origin feature/your-feature-name
```

Then create a PR on GitHub.

## Code Style Guidelines

### Python

- **Style**: Follow [PEP 8](https://pep8.org/)
- **Formatter**: Use `black` (line length: 100)
- **Linter**: Use `ruff`
- **Type Hints**: Required for all functions
- **Docstrings**: Google style for all public APIs

Example:

```python
def commit(
    self, message: str, prompt_data: Union[Dict[str, Any], Prompt], author: str = "system"
) -> PromptCommit:
    """
    Create a new commit with the given prompt.
    
    Args:
        message: Commit message describing the change
        prompt_data: Prompt data (dict or Prompt object)
        author: Author of the commit
        
    Returns:
        Created PromptCommit object
        
    Raises:
        ValueError: If repository doesn't exist
    """
    # Implementation here
    pass
```

### TypeScript

- **Style**: Follow [TypeScript best practices](https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html)
- **Formatter**: Prettier
- **Linter**: ESLint
- **Type Safety**: Strict mode enabled
- **Comments**: TSDoc for public APIs

Example:

```typescript
/**
 * Create a new commit with the given prompt.
 * 
 * @param message - Commit message describing the change
 * @param promptData - Prompt data object
 * @param author - Author of the commit
 * @returns Promise resolving to created commit
 */
async commit(
  message: string,
  promptData: PromptData,
  author: string = 'system'
): Promise<Commit> {
  // Implementation here
}
```

## Testing Guidelines

### Writing Tests

- **Unit Tests**: Test individual functions/classes
- **Integration Tests**: Test complete workflows
- **Test Coverage**: Aim for >80% coverage

### Python Test Example

```python
import pytest
from prompt_versioning.core import PromptRepository

def test_commit_creates_version(temp_repo):
    """Test that commit creates a new version."""
    repo = PromptRepository.init(temp_repo)
    
    commit = repo.commit("Test", {"system": "Test prompt"})
    
    assert commit.hash
    assert commit.message == "Test"
    
    versions = repo.log()
    assert len(versions) == 1
```

### TypeScript Test Example

```typescript
import { PromptRepository } from '../src';

describe('PromptRepository', () => {
  it('should create a commit', async () => {
    const repo = await PromptRepository.init('./test-repo');
    
    const commit = await repo.commit('Test', {
      system: 'Test prompt'
    });
    
    expect(commit.hash).toBeDefined();
    expect(commit.message).toBe('Test');
  });
});
```

## Documentation

### Adding Documentation

- Update relevant `.md` files in `docs/`
- Include code examples
- Keep language clear and concise

### Documentation Structure

- **README.md**: Overview and quick start
- **docs/CLI_REFERENCE.md**: Complete CLI documentation
- **docs/YAML_SCHEMA.md**: Prompt file format
- **docs/GITHUB_ACTIONS.md**: CI/CD integration
- **docs/COMPLIANCE_AUDIT.md**: Audit trail usage

## Pull Request Process

### Before Submitting

- [ ] Tests pass locally
- [ ] Code is formatted (black, prettier)
- [ ] Linters pass (ruff, eslint)
- [ ] Documentation is updated
- [ ] Commit messages follow conventions

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How to test these changes

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Changelog updated
```

### Review Process

1. Automated checks run (CI/CD)
2. Maintainer reviews code
3. Address feedback
4. Approval and merge

## Release Process

Releases are automated via GitHub Actions when tags are pushed.

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes

### Creating a Release

1. Update version in `pyproject.toml` and `package.json`
2. Update `CHANGELOG.md`
3. Create and push tag:

```bash
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0
```

4. GitHub Actions will publish to PyPI and npm

## Issue Reporting

### Bug Reports

Use the bug report template and include:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment (OS, Python/Node version)
- Error messages

### Feature Requests

Use the feature request template and include:
- Problem description
- Proposed solution
- Alternative solutions
- Additional context

## Community

- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Report bugs and request features
- **PRs**: Submit code contributions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Check existing [issues](https://github.com/yourusername/prompt-versioning-cli/issues)
- Ask in [discussions](https://github.com/yourusername/prompt-versioning-cli/discussions)
- Email: support@promptvc.dev

---

Thank you for contributing! 🎉

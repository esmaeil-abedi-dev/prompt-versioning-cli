# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-11-16

### Added

- File path tracking in commits - commits now store the source file path
- Automatic file restoration in `checkout` command
- File path display in `log` command output (both normal and `--oneline` modes)
- File path display in `status` command output
- `--no-write` option to `checkout` command for viewing without writing

### Changed

- `checkout` command now automatically restores files to their original location
- `checkout` command no longer prompts for filename when file path is known from commit
- Documentation updates to remove incorrect `--name` and `--non-interactive` flags
- Documentation updates to remove incorrect `--limit` flag (correct: `--max-count` or `-n`)
- Documentation updates to add missing `--no-write` option for checkout

### Fixed

- Checkout behavior now matches Git semantics - only restores the committed file
- Documentation inconsistencies across README, USER_GUIDE, QUICKSTART, and other docs

## [0.1.0] - Initial Release

### Added

- Initial project setup and structure
- Python package implementation with core functionality
- TypeScript/Node.js bindings
- CLI commands (init, commit, log, diff, checkout, tag, audit)
- MCP (Model Context Protocol) server support
- Agent system with multiple LLM backend support (OpenAI, Anthropic, Ollama)
- Comprehensive test suite
- Documentation (README, User Guide, Developer Guide, Contributing Guidelines)
- GitHub Actions CI/CD pipeline
- Code of Conduct and Security Policy

### Fixed

- Python linting errors (whitespace and code style issues)
- TypeScript build configuration
- Added package-lock.json for reproducible npm builds

### Infrastructure

- Set up GitHub Actions workflow for Python and TypeScript
- Configured Ruff linter for Python code quality
- Added test coverage reporting

## [1.0.0] - TBD

Initial release (not yet published). Package will be released once core features are stable and tested.

### Planned for Initial Release

- Core version control functionality (init, commit, log, diff, checkout)
- Experiment tagging with metadata
- Audit log generation (JSON and CSV formats)
- Python library and CLI
- TypeScript/Node.js bindings
- Semantic diffing for prompts
- Content-addressable storage
- Git-like UX (HEAD, HEAD~N references, short hashes)
- Complete documentation (CLI reference, YAML schema, GitHub Actions integration, compliance guide)
- Test suite with >80% coverage
- Published to PyPI and npm registries

## [Future Enhancements]

### Post 1.0 Roadmap

- Remote repository sync (like Git remotes)
- Branch support for parallel experiments
- Web UI for visual diff viewing
- Integration with LangSmith
- Integration with Weights & Biases
- Automated prompt performance tracking
- Merge conflict resolution
- Cherry-pick commits
- Interactive rebase
- Stash functionality

---

<!-- Links will be updated when versions are released -->

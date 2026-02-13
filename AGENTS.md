# AI Agent Instructions

This file contains instructions for AI coding agents working in this repository.

## Project Overview

This is a repository of rules, guides, and agent personas for AI coding agents.
It contains documentation and templates to ensure code quality and consistency
across different programming languages and frameworks.

## Commands

### Linting

```bash
# Lint all Markdown files
npx markdownlint-cli2 "**/*.md"

# Auto-fix Markdown issues
npx markdownlint-cli2 --fix "**/*.md"

# Run ShellCheck on shell scripts (if any)
shellcheck <script.sh>
```

### Git Operations

```bash
# Check current branch (should NOT be main)
git branch --show-current

# Create a feature branch
git checkout -b feature/my-feature

# Stage and commit changes
git add .
git commit -m "type(scope): description"

# Push to remote
git push -u origin <branch-name>

# Create a pull request
gh pr create --title "type: description" --body "..."
```

## Project Structure

```text
.
├── AGENTS.md          # This file - instructions for AI agents
├── README.md          # Project overview
├── .markdownlint.json # Markdown linting configuration
├── rules/             # Code style & linting rules
├── agents/            # AI agent personas
├── guides/            # Process & workflow guides
└── .github/
    └── workflows/
        └── lint.yml   # CI workflow
```

## Rules Reference

Always follow the relevant rule files when working with specific languages or tools:

- [Markdown](./rules/markdown.md) - Markdown formatting and linting rules
- [Git](./rules/git.md) - Git workflow, commit conventions, and branching
- [GitHub](./rules/github.md) - PR workflow, code review, and CLI usage
- [Bash](./rules/bash.md) - Shell scripting best practices
- [Python](./rules/python.md) - Python style, type hints, and testing
- [Rust](./rules/rust.md) - Rust patterns, error handling, and structure

## Agent Personas

Refer to these files for specialized agent instructions:

- [Code Reviewer](./agents/code-reviewer.md) - Review code for bugs and best practices
- [Navigation](./agents/navigation.md) - Explore and navigate codebases
- [Research](./agents/research.md) - Conduct research and gather information

## Guides

- [Documentation](./guides/documentation.md) - Create and maintain project documentation
- [New Project](./guides/new-project.md) - Scaffold and initialize new projects

## Quick Reference

### Commit Messages

Follow conventional commits format (see [Git Rules](./rules/git.md) for details):

```text
<type>(<scope>): <description>

Types: feat, fix, docs, style, refactor, test, chore
```

### Branch Naming

Use prefixes (see [Git Rules](./rules/git.md) for details):

- `feature/` - New features
- `fix/` - Bug fixes
- `refactor/` - Code restructuring
- `docs/` - Documentation updates

### Key Git Rules

1. **Never commit directly to main** - Always create a feature branch
2. **Pull requests required** - All changes must go through a PR
3. **Run linting before committing** - `markdownlint-cli2 "**/*.md"`

## File Organization

### Adding New Rules

1. Create file in `rules/` directory following `rules/template.md`
2. Update `README.md` to include the new rule file
3. Run `markdownlint-cli2` to verify formatting

### Adding New Agents

1. Create file in `agents/` directory with standard sections:
   - Purpose, Capabilities, Behavior, Process, Output Format
2. Update `README.md` to reference the new agent

## Configuration

- **Markdown Linting**: See `.markdownlint.json` for configuration
- **CI/CD**: See `.github/workflows/lint.yml` for workflow details

All linting must pass before merging.

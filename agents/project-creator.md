# Project Creator Agent

## Purpose

Create new projects with proper directory structure, configuration files, and an
AGENTS.md that references the applicable rules from the agent-files repository.

## Behavior

When asked to create a project (e.g., "Create a rust project", "Create a python
project called myapp"):

1. **Determine project type** from the request (python, rust, nodejs, bash, etc.)
2. **Create directory structure** following `guides/new-project.md` templates
3. **Create AGENTS.md** with references to applicable rules from this repository
4. **Initialize git** and create initial commit

## Repository References

All rule references should use the raw GitHub URL:

```text
https://github.com/gdellis/agent-files/raw/refs/heads/main/
```

## Project Templates

### Python Project

**Directory Structure:**

```text
project-name/
├── src/
│   └── project_name/
│       ├── __init__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── pyproject.toml
├── README.md
├── AGENTS.md
├── LICENSE
└── .gitignore
```

**AGENTS.md Content (Python):**

- Include README header and project overview
- Development commands: `uv venv`, `pytest`, `ruff check .`, `mypy src/`
- Git operations template
- Link to Python rules, Git rules, Markdown rules (using raw GitHub URLs)
- Code style: type hints, black (88 chars), isort, pytest
- Key rules: no main commits, lint before commit, >80% test coverage

---

### Node.js/TypeScript Project

**Directory Structure:**

```text
project-name/
├── src/
│   └── index.ts
├── tests/
│   └── index.test.ts
├── package.json
├── tsconfig.json
├── README.md
├── AGENTS.md
├── LICENSE
└── .gitignore
```

**AGENTS.md Content (Node.js):**

- Include README header and project overview
- Development commands: `npm install`, `npm run build`, `npm test`, `npm run lint`
- Git operations template
- Link to Git rules, Markdown rules (using raw GitHub URLs)
- Code style: TypeScript strict mode, ES modules, const over let, async/await
- Key rules: no main commits, lint before commit, write tests

---

### Rust Project

**Directory Structure:**

```text
project-name/
├── src/
│   ├── lib.rs
│   └── main.rs
├── tests/
│   └── integration_test.rs
├── Cargo.toml
├── README.md
├── AGENTS.md
├── LICENSE
└── .gitignore
```

**AGENTS.md Content (Rust):**

- Include README header and project overview
- Development commands: `cargo build`, `cargo run`, `cargo test`, `cargo clippy`,
  `cargo fmt`, `cargo check`
- Git operations template
- Link to Rust rules, Git rules, Markdown rules (using raw GitHub URLs)
- Code style: cargo fmt, cargo clippy, Result<T, E> over panics, doc comments
- Key rules: no main commits, clippy before commit, write tests

---

### Bash Project

**Directory Structure:**

```text
project-name/
├── src/
│   └── main.sh
├── tests/
│   └── test_main.bats
├── README.md
├── AGENTS.md
├── LICENSE
└── .gitignore
```

**AGENTS.md Content (Bash):**

- Include README header and project overview
- Development commands: `./src/main.sh`, `bats tests/`, `shellcheck src/*.sh`
- Git operations template
- Link to Bash rules, Git rules, Markdown rules (using raw GitHub URLs)
- Code style: `set -euo pipefail`, quote variables, `[[ ]]` for tests, printf
- Key rules: no main commits, shellcheck before commit, use strict mode

---

## AGENTS.md Template Structure

All AGENTS.md files should follow this structure:

```markdown
# AI Agent Instructions

This file contains instructions for AI coding agents working in this repository.

## Project Overview

[Brief description]

## Commands

### Development

[Language-specific commands]

### Git Operations

[Standard git workflow]

## Rules Reference

- [Language Rules](https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/<lang>.md)
- [Git Rules](https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/git.md)
- [Markdown Rules](https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/markdown.md)

## Code Style

[Language-specific style points]

## Key Rules

1. Never commit directly to main
2. Run linting before committing
3. Write tests for new features
```

---

## Process

1. **Parse request** to determine project type and name
2. **Create directory** with proper structure
3. **Write configuration files** (pyproject.toml, package.json, Cargo.toml, etc.)
4. **Create AGENTS.md** with appropriate rules references
5. **Create README.md** with basic project info
6. **Create .gitignore** for the language
7. **Create LICENSE** (MIT by default)
8. **Initialize git** and make initial commit

## Output Format

After creating the project, provide:

```text
Created <project-name> (<type>)

Project structure:
<src/
  ...>
Configuration:
- <config-file>
- AGENTS.md
- README.md
- LICENSE
- .gitignore

Next steps:
1. cd <project-name>
2. <install-dependencies-command>
3. <run-tests-command>
```

## What NOT to Do

- Don't skip AGENTS.md creation
- Don't forget to initialize git
- Don't use relative paths in AGENTS.md rule references (use raw GitHub URLs)
- Don't omit the LICENSE file

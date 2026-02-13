# Bootstrap Agent

## Purpose

Set up AI agent rules for existing projects by creating an AGENTS.md file that
references rules from the agent-files repository.

## Behavior

When asked to bootstrap a project:

1. **Detect project type** from existing files
2. **Create AGENTS.md** with rules references and project-specific commands
3. **Optionally update .gitignore** if missing language-specific entries

## Repository URL

All rule references should use the raw GitHub URL:

```text
https://github.com/gdellis/agent-files/raw/refs/heads/main/
```

## Project Detection

Detect project type by checking for these files:

| File | Project Type |
| ---- | ------------ |
| `pyproject.toml`, `setup.py`, `requirements.txt` | Python |
| `Cargo.toml` | Rust |
| `package.json` | Node.js/TypeScript |
| `go.mod` | Go |
| `*.sh` files in `src/` or root | Bash |
| `Makefile` | C/C++ or general |

## AGENTS.md Template Structure

All AGENTS.md files should follow this structure:

### Header Section

```markdown
# AI Agent Instructions

This file contains instructions for AI coding agents working in this repository.

## Project Overview

[Project name and brief description]
```

### Commands Section

Include language-specific development commands and standard git operations.

### Rules Reference Section

Include links to relevant rules using raw GitHub URLs. For Python:

```markdown
## Rules Reference

Follow these rules when working in this repository:

- [Python Rules](https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/python.md)
- [Git Rules](https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/git.md)
- [Markdown Rules](https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/markdown.md)
```

### Code Style Section

Summarize key style points from the language rules.

### Key Rules Section

List the most important rules to remember.

---

## Rules References by Language

### Python

- Python Rules: <https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/python.md>
- Git Rules: <https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/git.md>
- Markdown Rules: <https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/markdown.md>

**Key Style Points:** Type hints, black (88 chars), isort, pytest

**Commands:** `uv venv`, `pytest`, `ruff check .`, `mypy src/`

---

### Rust

- Rust Rules: <https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/rust.md>
- Git Rules: <https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/git.md>
- Markdown Rules: <https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/markdown.md>

**Key Style Points:** `cargo fmt`, `cargo clippy`, Result over panics, doc comments

**Commands:** `cargo build`, `cargo test`, `cargo clippy`, `cargo fmt`

---

### Node.js/TypeScript

- Git Rules: <https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/git.md>
- Markdown Rules: <https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/markdown.md>

**Key Style Points:** TypeScript strict, ES modules, const over let, async/await

**Commands:** `npm install`, `npm test`, `npm run lint`

---

### Bash

- Bash Rules: <https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/bash.md>
- Git Rules: <https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/git.md>
- Markdown Rules: <https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/markdown.md>

**Key Style Points:** `set -euo pipefail`, quote variables, `[[ ]]` for tests, printf

**Commands:** `./src/main.sh`, `bats tests/`, `shellcheck src/*.sh`

---

## Process

1. **Detect project type** by looking for configuration files
2. **Read existing project info** (README, package.json, Cargo.toml, etc.) for
   project name and description
3. **Check for existing AGENTS.md** - ask before overwriting
4. **Create AGENTS.md** using the appropriate template
5. **Check .gitignore** - add missing entries if needed

## gitignore Entries to Add

### Python

```text
__pycache__/
*.py[cod]
.venv/
venv/
*.egg-info/
dist/
build/
.pytest_cache/
```

### Rust

```text
/target/
Cargo.lock
```

### Node.js

```text
node_modules/
dist/
*.log
```

### Bash

```text
# No specific entries needed
```

## Output Format

After bootstrapping, provide:

```text
Bootstrapped <project-type> project with AI agent rules.

Created:
- AGENTS.md

Updated (if needed):
- .gitignore (added <language> entries)

Rules included:
- <Language> Rules
- Git Rules
- Markdown Rules

Next steps:
1. Review AGENTS.md and customize project-specific commands
2. Ensure test/lint commands match your project's setup
```

## What NOT to Do

- Don't overwrite AGENTS.md without asking
- Don't remove existing .gitignore entries
- Don't assume commands exist (check package.json, Cargo.toml, etc.)
- Don't use relative paths in rule references

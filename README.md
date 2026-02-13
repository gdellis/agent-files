# AI Agent Rules Repository

This repository contains reference files and rule sets for AI agents to ensure
code quality, consistency, and adherence to best practices across different
programming languages and frameworks.

Repository: <https://github.com/gdellis/agent-files>

## How to Use

### Referencing Rules in Prompts

Use the raw GitHub URLs to reference rules in your AI prompts. This ensures the
agent can access the latest version of the rules:

```text
https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/<file>.md
```

**Example Prompts:**

Write a Python REST API following the rules in:

`https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/python.md`

Review this code for bugs and style issues following:

`https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/rust.md`

Create a bash script to deploy the application, following:

`https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/bash.md`

### Using Agent Personas

Agent personas are specialized instructions for specific tasks. Reference them
in your prompts:

**Code Reviewer:**

Review this pull request as a code reviewer following `https://github.com/gdellis/agent-files/raw/refs/heads/main/agents/code-reviewer.md`

**Navigation:**

Find all API endpoints in this codebase following `https://github.com/gdellis/agent-files/raw/refs/heads/main/agents/navigation.md`

**Research:**

Research best practices for WebSocket implementation following `https://github.com/gdellis/agent-files/raw/refs/heads/main/agents/research.md`

**Project Creator:**

Create a new Rust project called 'my-cli' following `https://github.com/gdellis/agent-files/raw/refs/heads/main/agents/project-creator.md`

**Bootstrap (for existing projects):**

Bootstrap this project with agent rules from `https://github.com/gdellis/agent-files/raw/refs/heads/main/agents/bootstrap.md`

### Bootstrapping an Existing Project

To set up AI agent rules for an existing project, ask your AI agent to:

1. Detect the project type (Python, Rust, Node.js, Bash, etc.)
2. Create an `AGENTS.md` file in the project root
3. Include references to relevant rules using raw GitHub URLs

**Example prompt:**

Bootstrap this project with agent rules using `https://github.com/gdellis/agent-files/raw/refs/heads/main/agents/bootstrap.md`

The resulting `AGENTS.md` will contain:

- Project-specific commands (build, test, lint)
- Links to relevant rules (language, git, markdown)
- Code style guidelines
- Key rules summary

### Quick Reference URLs

| Type | URL |
| ---- | --- |
| Bash Rules | <https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/bash.md> |
| Python Rules | <https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/python.md> |
| Rust Rules | <https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/rust.md> |
| Markdown Rules | <https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/markdown.md> |
| Git Rules | <https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/git.md> |
| GitHub Rules | <https://github.com/gdellis/agent-files/raw/refs/heads/main/rules/github.md> |

## Available Rules

- [Bash](./rules/bash.md) - Best practices for shell scripting, focusing on safety
  and portability.
- [Git](./rules/git.md) - Commit conventions, branching strategies, and git workflows.
- [GitHub](./rules/github.md) - PR workflows, code review, and GitHub CLI usage.
- [Python](./rules/python.md) - PEP 8 style, type hints, testing with pytest, and
  dependency management.
- [Rust](./rules/rust.md) - Idiomatic Rust patterns, error handling, and project structure.
- [Markdown](./rules/markdown.md) - Rules for documentation consistency and `markdownlint`.

## Agent Personas

- [Code Reviewer](./agents/code-reviewer.md) - Review code changes for bugs and best practices.
- [Navigation](./agents/navigation.md) - Explore and navigate codebases efficiently.
- [Research](./agents/research.md) - Conduct research and gather information.
- [Project Creator](./agents/project-creator.md) - Create new projects with proper structure and rules.
- [Bootstrap](./agents/bootstrap.md) - Set up AI agent rules for existing projects.

## Guides

- [Documentation](./guides/documentation.md) - Create and maintain project documentation.
- [New Project](./guides/new-project.md) - Scaffold and initialize new projects.

## Structure

```text
.
├── AGENTS.md          # Instructions for AI agents working in this repo
├── README.md          # This file
├── rules/             # Code style & linting rules
│   ├── bash.md
│   ├── git.md
│   ├── github.md
│   ├── markdown.md
│   ├── python.md
│   ├── rust.md
│   └── template.md
├── agents/            # AI agent personas
│   ├── bootstrap.md
│   ├── code-reviewer.md
│   ├── navigation.md
│   ├── project-creator.md
│   └── research.md
├── guides/            # Process & workflow guides
│   ├── documentation.md
│   └── new-project.md
└── .github/
    └── workflows/
        └── lint.yml
```

Each rule file follows a standard structure defined in [`rules/template.md`](./rules/template.md):

- **Core Mandates**: Non-negotiable rules (safety, strict mode).
- **Style**: Naming, formatting.
- **Error Handling**: How to manage failures.
- **Testing**: Testing frameworks and patterns.

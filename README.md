# AI Agent Rules Repository

This repository contains reference files and rule sets for AI agents to ensure
code quality, consistency, and adherence to best practices across different
programming languages and frameworks.

## Usage

When prompting an AI agent, you can refer it to the specific file for the task.

**Example Prompts:**
> "Please write a bash script to backup files, following the rules in `rules/bash.md`."
> "Review this PR as a code-reviewer agent following `agents/code-reviewer.md`."
> "Create documentation for this project following `guides/documentation.md`."

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

## Guides

- [Documentation](./guides/documentation.md) - Create and maintain project documentation.

## Structure

```text
.
├── README.md
├── rules/           # Code style & linting rules
│   ├── bash.md
│   ├── git.md
│   ├── github.md
│   ├── markdown.md
│   ├── python.md
│   ├── rust.md
│   └── template.md
├── agents/          # AI agent personas
│   ├── code-reviewer.md
│   ├── navigation.md
│   └── research.md
├── guides/          # Process & workflow guides
│   └── documentation.md
└── .github/
    └── workflows/
        └── lint.yml
```

Each rule file follows a standard structure defined in [`rules/template.md`](./rules/template.md):

- **Core Mandates**: Non-negotiable rules (safety, strict mode).
- **Style**: Naming, formatting.
- **Error Handling**: How to manage failures.
- **Testing**: Testing frameworks and patterns.

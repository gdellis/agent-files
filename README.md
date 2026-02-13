# AI Agent Rules Repository

This repository contains reference files and rule sets for AI agents to ensure
code quality, consistency, and adherence to best practices across different
programming languages and frameworks.

## Usage

When prompting an AI agent, you can refer it to the specific file for the language
you are working with.

**Example Prompt:**
> "Please write a bash script to backup files, following the rules in `rules/bash.md`."

## Available Rules

- [Bash](./rules/bash.md) - Best practices for shell scripting, focusing on safety
  and portability.
- [Git](./rules/git.md) - Commit conventions, branching strategies, and git workflows.
- [GitHub](./rules/github.md) - PR workflows, code review, and GitHub CLI usage.
- [Python](./rules/python.md) - PEP 8 style, type hints, testing with pytest, and
  dependency management.
- [Rust](./rules/rust.md) - Idiomatic Rust patterns, error handling, and project structure.
- [Markdown](./rules/markdown.md) - Rules for documentation consistency and `markdownlint`.

## Structure

```text
.
├── README.md
├── rules/
│   ├── bash.md
│   ├── git.md
│   ├── github.md
│   ├── markdown.md
│   ├── python.md
│   ├── rust.md
│   └── template.md
└── .github/
    └── workflows/
        └── lint.yml
```

Each rule file follows a standard structure defined in [`rules/template.md`](./rules/template.md):

- **Core Mandates**: Non-negotiable rules (safety, strict mode).
- **Style**: Naming, formatting.
- **Error Handling**: How to manage failures.
- **Testing**: Testing frameworks and patterns.

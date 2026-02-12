# AI Agent Rules Repository

This repository contains reference files and rule sets for AI agents to ensure code quality, consistency, and adherence to best practices across different programming languages and frameworks.

## Usage

When prompting an AI agent, you can refer it to the specific file for the language you are working with.

**Example Prompt:**
> "Please write a bash script to backup files, following the rules in `ai-rules/bash.md`."

## Available Rules

- [Bash](./bash.md) - Best practices for shell scripting, focusing on safety and portability.
- [Rust](./rust.md) - Idiomatic Rust patterns, error handling, and project structure.

## Structure

Each language file follows a standard structure defined in [`template.md`](./template.md):
- **Core Mandates**: Non-negotiable rules (safety, strict mode).
- **Style**: Naming, formatting.
- **Error Handling**: How to manage failures.
- **Testing**: Testing frameworks and patterns.

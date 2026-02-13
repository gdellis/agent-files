# Markdown Rules for AI Agents

## Core Mandates

1. **Validation**: All Markdown documents must be valid according to [`markdownlint-cli2`](https://github.com/DavidAnson/markdownlint-cli2).
2. **Consistency**: Maintain consistent formatting for headers, lists, and code blocks throughout a document.
3. **Clarity**: Prefer clarity over brevity. Use descriptive headers and meaningful link text.
4. **Accessibility**: Always include alt text for images.

## Workflow

- **Installation**:

    ```bash
    npm install -g markdownlint-cli2
    ```

- **Validation**: Run on all Markdown files:

    ```bash
    markdownlint-cli2 "**/*.md"
    ```

- **Auto-fix**: Automatically fix issues where possible:

    ```bash
    markdownlint-cli2 --fix "**/*.md"
    ```

- **Pre-commit**: Validate staged files before committing:

    ```bash
    markdownlint-cli2 $(git diff --name-only --cached "*.md")
    ```

## Code Style & Structure

- **Headers** (MD003):
  - Use ATX headers (`# Header`) instead of Setext headers (`Header\n======`).
  - Ensure a single H1 header (`# Title`) per document (MD025).
  - Do not skip header levels (e.g., H2 to H4) (MD001).
- **Lists** (MD004):
  - Use hyphens `-` for unordered lists.
  - Use `1.` for ordered lists (unless auto-numbering is preferred, but specific numbers are safer for reference).
  - Indent list items by 2 spaces.
- **Code Blocks**:
  - Always specify the language for fenced code blocks (e.g., \`\`\`bash) (MD040).
  - Use 3 backticks for fencing code blocks.
- **Line Length** (MD013):
  - Aim for 80-120 characters per line for readability.
  - Long lines are acceptable for links or code blocks where wrapping is difficult.
- **Emphasis**:
  - Use asterisks `*` for italics and double asterisks `**` for bold.

## Configuration

Use a `.markdownlint-cli2.jsonc` configuration file in the project root:

```jsonc
{
  "config": {
    "default": true,
    "MD013": {
      "line_length": 120,
      "code_blocks": false,
      "tables": false
    },
    "MD024": {
      "siblings_only": true
    },
    "MD041": false
  }
}
```

## Key Rules Reference

For a complete list of all available rules and their configurations, see the
official [markdownlint Rules documentation](https://github.com/DavidAnson/markdownlint/blob/v0.40.0/doc/Rules.md).

### Commonly Used Rules

- **MD001/header-increment**: Header levels should only increment by one level at a time.
- **MD002/first-header-h1**: First header should be a top-level header.
- **MD003/header-style**: Header style. Expected: `atx`.
- **MD004/ul-style**: Unordered list style. Expected: `dash`.
- **MD009/no-trailing-spaces**: Trailing spaces. Expected: 0 or 2 (for line break).
- **MD012/no-multiple-blanks**: Multiple consecutive blank lines.
- **MD013/line-length**: Line length. (Relaxed to 120 chars).
- **MD022/blanks-around-headers**: Headers should be surrounded by blank lines.
- **MD025/single-title/single-h1**: Multiple top-level headers in the same document.
- **MD031/blanks-around-fences**: Fenced code blocks should be surrounded by blank lines.
- **MD032/blanks-around-lists**: Lists should be surrounded by blank lines.
- **MD040/fenced-code-language**: Fenced code blocks should have a language specified.
- **MD041/first-line-h1**: First line in file should be a top-level header.
- **MD047/single-trailing-newline**: Files should end with a single newline character.

### Table Rules

- **Table Formatting**: Always add spaces around pipes in tables for readability:

  ```markdown
  | Column 1 | Column 2 |
  | -------- | -------- |
  | Value 1  | Value 2  |
  ```

  Not:

  ```markdown
  |Column 1|Column 2|
  |--------|--------|
  |Value 1|Value 2|
  ```

## Best Practices

- **Links**: Use reference-style links for cleaner source text when URLs are long or repeated.

    ```markdown
    [Link Text][ref]

    [ref]: https://example.com
    ```

- **Tables**: Align columns for readability in raw text.

    ```markdown
    | Header 1 | Header 2 |
    | :------- | :------- |
    | Row 1    | Data 1   |
    ```

- **Comments**: Use HTML comments `<!-- comment -->` for internal notes not meant for rendering.

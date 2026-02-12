# Markdown Rules for AI Agents

## Core Mandates

1.  **Validation**: All Markdown documents must be valid according to `markdownlint` (or equivalent standard rules).
2.  **Consistency**: Maintain consistent formatting for headers, lists, and code blocks throughout a document.
3.  **Clarity**: Prefer clarity over brevity. Use descriptive headers and meaningful link text.
4.  **Accessibility**: Always include alt text for images.

## Code Style & Structure

-   **Headers**:
    -   Use ATX headers (`# Header`) instead of Setext headers (`Header\n======`).
    -   Ensure a single H1 header (`# Title`) per document.
    -   Do not skip header levels (e.g., H2 to H4).
-   **Lists**:
    -   Use hyphens `-` for unordered lists.
    -   Use `1.` for ordered lists (unless auto-numbering is preferred, but specific numbers are safer for reference).
    -   Indent list items by 2 spaces.
-   **Code Blocks**:
    -   Always specify the language for fenced code blocks (e.g., \`\`\`bash).
    -   Use 3 backticks for fencing code blocks.
-   **Line Length**:
    -   Aim for 80-120 characters per line for readability, unless it breaks a link or code block.
    -   Disable `MD013` (line length) if hard wrapping is not desired/enforced by tooling.
-   **Emphasis**:
    -   Use asterisks `*` for italics and double asterisks `**` for bold.

## Markdownlint Rules

-   **MD001/header-increment**: Header levels should only increment by one level at a time.
-   **MD002/first-header-h1**: First header should be a top-level header.
-   **MD003/header-style**: Header style. Expected: atx.
-   **MD004/ul-style**: Unordered list style. Expected: dash.
-   **MD009/no-trailing-spaces**: Trailing spaces. Expected: 0 or 2 (for line break).
-   **MD013/line-length**: Line length. (Often disabled or relaxed to 120 chars).
-   **MD022/blanks-around-headers**: Headers should be surrounded by blank lines.
-   **MD031/blanks-around-fences**: Fenced code blocks should be surrounded by blank lines.
-   **MD032/blanks-around-lists**: Lists should be surrounded by blank lines.
-   **MD041/first-line-h1**: First line in file should be a top-level header.

## Best Practices

-   **Links**: Use reference-style links for cleaner source text when URLs are long or repeated.
    ```markdown
    [Link Text][ref]

    [ref]: https://example.com
    ```
-   **Tables**: Align columns for readability in raw text.
    ```markdown
    | Header 1 | Header 2 |
    | :------- | :------- |
    | Row 1    | Data 1   |
    ```
-   **Comments**: Use HTML comments `<!-- comment -->` for internal notes not meant for rendering.

## Example Template

```markdown
# Document Title

## Introduction

This is a paragraph with **bold text** and *italic text*.

## Section 1

-   Item 1
-   Item 2

### Subsection

Here is a code block:

\`\`\`bash
echo "Hello World"
\`\`\`

## References

[Link to Google](https://google.com)
```

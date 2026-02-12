# Bash Scripting Rules for AI Agents

## Core Mandates

1.  **Strict Mode**: Always start scripts with `set -euo pipefail`.
    -   `e`: Exit immediately if a command exits with a non-zero status.
    -   `u`: Treat unset variables as an error.
    -   `o pipefail`: Return value of a pipeline is the status of the last command to exit with a non-zero status.
2.  **Safety**: Never use `rm -rf` without validating the path first. Prefer `rm` with specific files or use a trash utility if available in context.
3.  **Portability**: Prefer POSIX-compliant syntax where possible, unless Bash-specific features (arrays, process substitution) are required for clarity or performance.
4.  **Shebang**: Always use `#!/usr/bin/env bash` for portability.

## Code Style & Structure

-   **Indentation**: Use 2 spaces for indentation.
-   **Naming Conventions**:
    -   Variables: `UPPER_CASE` for exported/global constants, `lower_case` for local variables.
    -   Functions: `snake_case`.
-   **Quoting**: Always quote variables (`"$VAR"`) to prevent word splitting and globbing issues, unless you explicitly want that behavior.
-   **Structure**:
    1.  Shebang
    2.  `set -euo pipefail`
    3.  Constants/Configuration
    4.  Functions
    5.  `main` function
    6.  `if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then main "$@"; fi`

## Error Handling

-   **Checks**: Check for command success explicitly if not covered by `set -e`.
-   **Cleanup**: Use `trap` for cleanup of temporary files/directories.
    ```bash
    trap 'rm -f "$temp_file"' EXIT
    ```
-   **Messages**: Print error messages to stderr: `echo "Error: ..." >&2`.

## Best Practices

-   **`[[ ]]` over `[ ]`**: Use double brackets `[[ ... ]]` for tests; they are safer and more powerful.
-   **`printf` over `echo`**: Use `printf` for safer and more consistent output formatting.
-   **Local Variables**: Declare function variables as `local` to avoid polluting the global scope.
-   **Command Substitution**: Use `$(...)` instead of backticks `` `...` ``.
-   **Static Analysis**: Always validate scripts with `shellcheck`. address all warnings or explicitly suppress them with a comment explaining why.

## ShellCheck Rules

-   **Validation**: Every script must pass `shellcheck` without errors before completion.
-   **Directives**: Use directives to suppress false positives only when necessary.
    ```bash
    # shellcheck disable=SC2034  # Unused variable intended for export
    export MY_VAR="value"
    ```
-   **Common Issues**:
    -   **SC2086** (Double quote to prevent globbing/word splitting): Always quote variables unless specific expansion is intended.
    -   **SC2006** (Use `$(...)` instead of legacy backticks): Modernize command substitution.
    -   **SC2155** (Declare and assign separately to avoid masking return values):
        ```bash
        # Bad
        local output=$(command)
        
        # Good
        local output
        output=$(command)
        ```

## Example Template

```bash
#!/usr/bin/env bash
set -euo pipefail

# Constants
readonly LOG_FILE="/var/log/myapp.log"

usage() {
  cat <<EOF
Usage: $(basename "${0}") [OPTIONS] <arg>
Description...
EOF
  exit 1
}

log_error() {
  printf "ERROR: %s\n" "$1" >&2
}

main() {
  local arg="${1:-}"

  if [[ -z "$arg" ]]; then
    usage
  fi

  # Your logic here
  printf "Processing: %s\n" "$arg"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
```

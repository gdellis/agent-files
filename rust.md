# Rust Rules for AI Agents

## Core Mandates

1.  **Safety**: Always prioritize memory safety and correctness. Avoid `unsafe` blocks unless absolutely necessary and thoroughly justified.
2.  **Strictness**: Adhere strictly to the borrow checker's rules. Avoid "fighting" it; instead, restructure code to be ownership-compliant.
3.  **Modern Idioms**: Use modern Rust idioms (edition 2021+), including `?` for error propagation, pattern matching, and iterators.
4.  **Formatting**: Always format code with `cargo fmt`.

## Code Style & Structure

-   **Indentation**: 4 spaces.
-   **Naming Conventions**:
    -   Types/Traits: `PascalCase`
    -   Functions/Methods/Modules/Variables: `snake_case`
    -   Constants/Statics: `SCREAMING_SNAKE_CASE`
-   **Imports**: Group imports logically (`std`, external crates, internal modules).
-   **File Organization**:
    -   Public items at the top.
    -   Implementation blocks grouped by type.
    -   Tests in a `tests` module at the bottom of the file (or separate files for integration tests).

## Error Handling

-   **Types**: Use `Result<T, E>` for recoverable errors and `Option<T>` for optional values. Avoid panicking (`unwrap`, `expect`) in library code or production paths.
-   **Crates**: Use `thiserror` for library error types and `anyhow` for application error handling (unless `std::error::Error` suffices).
-   **Propagation**: Use the `?` operator for concise error propagation.

## Testing

-   **Unit Tests**: Place unit tests in a `mod tests` block within the source file, annotated with `#[cfg(test)]`.
-   **Integration Tests**: Place integration tests in the `tests/` directory.
-   **Documentation Tests**: Include examples in doc comments (`///`) which are automatically tested.

## Best Practices

-   **Clippy**: Ensure code passes `cargo clippy` without warnings.
-   **Documentation**: Document public APIs with doc comments (`///`).
-   **Ownership**: Prefer passing by reference (`&T`) over cloning (`.clone()`) unless ownership transfer is required.
-   **Iterators**: Prefer iterator chains (`map`, `filter`, `fold`) over explicit loops for data transformation.
-   **Pattern Matching**: Use exhaustive `match` expressions or `if let` for robust control flow.

## Example Template

```rust
// src/lib.rs

use std::error::Error;

/// A simple function that adds two numbers.
///
/// # Examples
///
/// ```
/// let result = my_crate::add(2, 2);
/// assert_eq!(result, 4);
/// ```
pub fn add(left: usize, right: usize) -> usize {
    left + right
}

/// A custom error type.
#[derive(Debug)]
pub enum MyError {
    InvalidInput(String),
}

impl std::fmt::Display for MyError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            MyError::InvalidInput(msg) => write!(f, "Invalid input: {}", msg),
        }
    }
}

impl Error for MyError {}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}
```

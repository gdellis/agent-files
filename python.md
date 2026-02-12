# Python Rules for AI Agents

## Core Mandates

1. **Style**: Follow PEP 8 conventions. Format code with `black` and sort imports
   with `isort`.
2. **Typing**: Use type hints for all function signatures. Run `mypy` for static
   type checking.
3. **Safety**: Never use `eval()`, `exec()`, or handle user input without
   validation.
4. **Version**: Target Python 3.10+ syntax unless backward compatibility is
   required.

## Style & Formatting

- **Line Length**: 88 characters (black default).
- **Indentation**: 4 spaces, no tabs.
- **Imports**: Group and sort imports using `isort` with black-compatible settings:

  ```python
  # Standard library
  import os
  import sys

  # Third-party
  import requests

  # Local
  from myapp import utils
  ```

- **Naming Conventions**:
  - Functions/Variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `SCREAMING_SNAKE_CASE`
  - Private attributes: `_leading_underscore`

- **Docstrings**: Use triple-double quotes. Prefer Google style:

  ```python
  def calculate_sum(a: int, b: int) -> int:
      """Calculate the sum of two integers.

      Args:
          a: First integer.
          b: Second integer.

      Returns:
          The sum of a and b.
      """
      return a + b
  ```

## Error Handling

- **Exceptions**: Use specific exception types. Never use bare `except:`:

  ```python
  # Bad
  try:
      do_something()
  except:
      pass

  # Good
  try:
      do_something()
  except FileNotFoundError:
      logger.error("File not found")
      raise
  ```

- **Logging**: Use the `logging` module, not `print()`:

  ```python
  import logging

  logger = logging.getLogger(__name__)

  def process_data(data: dict) -> None:
      logger.info("Processing data: %s", data.get("id"))
  ```

- **Custom Exceptions**: Define custom exceptions for application-specific errors:

  ```python
  class AppError(Exception):
      """Base exception for application errors."""
      pass


  class ValidationError(AppError):
      """Raised when input validation fails."""
      pass
  ```

## Testing

- **Framework**: Use `pytest` for all tests.
- **Structure**: Place tests in a `tests/` directory mirroring the source
  structure:

  ```text
  src/
    myapp/
      utils.py
  tests/
    test_utils.py
  ```

- **Naming**: Test files start with `test_`. Test functions start with `test_`.
- **Fixtures**: Use pytest fixtures for common test setup:

  ```python
  import pytest

  @pytest.fixture
  def sample_data():
      return {"key": "value"}

  def test_process(sample_data):
      assert sample_data["key"] == "value"
  ```

- **Coverage**: Aim for >80% test coverage. Run with:

  ```bash
  pytest --cov=myapp tests/
  ```

## Dependency Management

- **Tool**: Use `uv` (preferred) or `poetry` for dependency management.
- **Virtual Environment**: Always use a virtual environment.
- **Requirements**:
  - `pyproject.toml` for project metadata and dependencies.
  - Pin versions for production: `requests==2.31.0`.
  - Use version ranges for libraries: `requests>=2.31,<3.0`.

- **Setup with uv**:

  ```bash
  uv venv
  source .venv/bin/activate
  uv pip install -e ".[dev]"
  ```

## Static Analysis Tools

Run these tools before committing:

- **black**: Format code.
- **isort**: Sort imports.
- **mypy**: Type checking.
- **ruff**: Fast linter (replacement for flake8, pydocstyle).

```bash
black .
isort .
mypy src/
ruff check .
```

## Best Practices

- **Context Managers**: Use `with` statements for resource management:

  ```python
  with open("file.txt", "r") as f:
      content = f.read()
  ```

- **f-strings**: Use f-strings for string formatting (Python 3.6+):

  ```python
  name = "Alice"
  greeting = f"Hello, {name}!"
  ```

- **Comprehensions**: Prefer comprehensions over map/filter for readability:

  ```python
  # Good
  squares = [x**2 for x in range(10)]
  even = {x for x in range(10) if x % 2 == 0}
  ```

- **Type Guards**: Use `isinstance()` for type checking:

  ```python
  def process(value: int | str) -> str:
      if isinstance(value, int):
          return str(value)
      return value.upper()
  ```

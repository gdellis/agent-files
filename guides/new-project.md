# New Project Guide

This guide provides templates and best practices for scaffolding new projects.

## General Best Practices

### Before Starting

1. **Check if a project already exists** - Search GitHub, npm, PyPI, crates.io
2. **Choose a descriptive name** - Lowercase, hyphen-separated, no special characters
3. **Initialize git immediately** - `git init` before any code
4. **Set up `.gitignore`** - Use templates from [gitignore.io](https://gitignore.io)

### Essential Files

Every project should have:

- `README.md` - Project overview, installation, usage
- `LICENSE` - MIT, Apache-2.0, or GPL-3.0
- `.gitignore` - Language-specific ignores
- `CHANGELOG.md` - Version history (for libraries/tools)

### README Structure

```markdown
# Project Name

Brief description.

## Features

- Feature 1
- Feature 2

## Installation

pip install project-name

## Usage

Basic usage examples.

## Development

How to set up development environment.

## License

MIT
```

---

## Python Projects

### Project Structure

```text
project-name/
├── src/
│   └── project_name/
│       ├── __init__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

### Setup Commands

```bash
# Create project directory
mkdir project-name && cd project-name

# Initialize git
git init

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Create src structure
mkdir -p src/project_name tests

# Create essential files
touch src/project_name/__init__.py
touch src/project_name/main.py
touch tests/__init__.py
touch tests/test_main.py

# Initialize project with uv
uv init

# Install dev dependencies
uv pip install pytest ruff mypy
```

### pyproject.toml Template

```toml
[project]
name = "project-name"
version = "0.1.0"
description = "Brief description"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.10"
dependencies = []

[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 88
target-version = "py310"

[tool.mypy]
python_version = "3.10"
strict = true
```

### .gitignore Template

```text
# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
*.egg-info/
dist/
build/
.eggs/

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp
```

---

## Node.js/TypeScript Projects

### Project Structure

```text
project-name/
├── src/
│   └── index.ts
├── tests/
│   └── index.test.ts
├── package.json
├── tsconfig.json
├── README.md
├── LICENSE
└── .gitignore
```

### Setup Commands

```bash
# Create project directory
mkdir project-name && cd project-name

# Initialize git
git init

# Initialize npm
npm init -y

# Install TypeScript
npm install -D typescript @types/node

# Create src structure
mkdir src tests
touch src/index.ts

# Initialize TypeScript
npx tsc --init

# Install dev dependencies
npm install -D vitest eslint prettier
```

### package.json Template

```json
{
  "name": "project-name",
  "version": "0.1.0",
  "description": "Brief description",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "test": "vitest",
    "lint": "eslint src/",
    "format": "prettier --write src/"
  },
  "keywords": [],
  "license": "MIT",
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0",
    "vitest": "^1.0.0"
  }
}
```

### tsconfig.json Template

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "declaration": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### .gitignore Template

```text
# Dependencies
node_modules/

# Build
dist/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*
```

---

## Rust Projects

### Project Structure

```text
project-name/
├── src/
│   ├── lib.rs
│   └── main.rs
├── tests/
│   └── integration_test.rs
├── Cargo.toml
├── README.md
├── LICENSE
└── .gitignore
```

### Setup Commands

```bash
# Create project with cargo
cargo new project-name
cd project-name

# Initialize git (cargo does this automatically)
git init

# Create lib file for library projects
touch src/lib.rs

# Create tests directory
mkdir tests
touch tests/integration_test.rs
```

### Cargo.toml Template

```toml
[package]
name = "project-name"
version = "0.1.0"
edition = "2021"
description = "Brief description"
license = "MIT"
repository = "https://github.com/user/project-name"

[dependencies]

[dev-dependencies]

[profile.release]
lto = true
strip = true
```

### .gitignore Template

```text
# Build
/target/

# IDE
.vscode/
.idea/

# OS
.DS_Store
```

---

## Bash Projects

### Project Structure

```text
project-name/
├── src/
│   └── main.sh
├── tests/
│   └── test_main.bats
├── README.md
├── LICENSE
└── .gitignore
```

### Setup Commands

```bash
# Create project directory
mkdir -p project-name/src project-name/tests
cd project-name

# Initialize git
git init

# Create main script
cat > src/main.sh << 'EOF'
#!/usr/bin/env bash
set -euo pipefail

main() {
    echo "Hello, World!"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
EOF

chmod +x src/main.sh

# Install bats for testing (if needed)
# See: https://github.com/bats-core/bats-core
```

### .gitignore Template

```text
# No build artifacts for bash
# Add any generated files

# IDE
.vscode/
.idea/

# OS
.DS_Store
```

---

## Quick Reference

| Language | Package Manager | Config File | Test Runner |
| -------- | --------------- | ----------- | ----------- |
| Python | uv/pip | pyproject.toml | pytest |
| Node.js | npm/pnpm | package.json | vitest/jest |
| Rust | cargo | Cargo.toml | cargo test |
| Bash | N/A | N/A | bats |

## Next Steps After Scaffold

1. Write initial code in `src/`
2. Add tests in `tests/`
3. Set up CI/CD in `.github/workflows/`
4. Configure linting/formatting tools
5. Write comprehensive README
6. Add LICENSE file

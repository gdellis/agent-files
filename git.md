# Git Rules for AI Agents

## Core Mandates

1. **Atomic Commits**: Each commit should represent a single logical change.
   Avoid mixing unrelated changes in one commit.
2. **Descriptive Messages**: Write clear, concise commit messages that explain
   the "why" not the "what".
3. **Clean History**: Prefer rebase over merge for local branches. Keep history
   readable.
4. **Never Force Push**: Never use `--force` on shared branches. Use
   `--force-with-lease` only when absolutely necessary.

## Commit Messages

Follow the conventional commits format:

```text
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting, semicolons, whitespace
- `refactor`: Code restructuring without behavior change
- `test`: Adding or updating tests
- `chore`: Build, CI, dependency updates

**Examples**:

```text
feat(auth): add OAuth2 login support

fix(api): handle null response from user endpoint

docs(readme): update installation instructions
```

## Branch Naming

Use descriptive branch names with prefixes:

- `feature/` - New features: `feature/user-authentication`
- `fix/` - Bug fixes: `fix/login-timeout`
- `refactor/` - Code refactoring: `refactor/payment-module`
- `docs/` - Documentation: `docs/api-reference`

## Workflow

### Starting Work

```bash
# Update main branch
git checkout main
git pull --rebase

# Create feature branch
git checkout -b feature/my-feature
```

### Making Commits

```bash
# Stage specific changes
git add -p

# Commit with message
git commit -m "feat(module): add new functionality"

# Or use editor for longer messages
git commit
```

### Keeping Branch Updated

```bash
# Rebase onto updated main
git fetch origin
git rebase origin/main
```

### Before Pushing

```bash
# Review changes
git log origin/main..HEAD --oneline
git diff origin/main...HEAD

# Run tests/linting
npm test
npm run lint
```

## Best Practices

- **Pull Requests**: Create PRs for all changes to main/master branches.
- **Review Your Own Diff**: Always review your changes with `git diff` before
  committing.
- **Avoid Large PRs**: Keep changes focused. If a PR exceeds 400 lines, consider
  splitting.
- **Don't Commit Secrets**: Never commit `.env`, credentials, API keys, or
  passwords. Use `.gitignore`.
- **Use `.gitignore`**: Ignore generated files, dependencies, IDE settings, and
  secrets.

## Common Commands

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Amend last commit message (only if not pushed)
git commit --amend -m "New message"

# Interactive rebase for last N commits
git rebase -i HEAD~3

# Cherry-pick specific commit
git cherry-pick <commit-hash>

# Stash changes
git stash push -m "description"
git stash pop

# Find which commit introduced a bug
git bisect start
git bisect bad
git bisect good <known-good-commit>
```

## Git Hooks

Use hooks to enforce quality:

- **pre-commit**: Run linters, formatters
- **pre-push**: Run tests
- **commit-msg**: Validate commit message format

Consider using [pre-commit](https://pre-commit.com/) framework for managing hooks.

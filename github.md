# GitHub Rules for AI Agents

## Core Mandates

1. **Pull Requests**: All changes to main/master must go through a pull request.
2. **Descriptive PRs**: Use clear titles and descriptions. Explain the "why".
3. **Small PRs**: Keep pull requests focused and reviewable (ideally <400 lines).
4. **Clean Branches**: Delete branches after merging.

## Pull Request Workflow

### Creating a PR

```bash
# Push branch to origin
git push -u origin feature/my-feature

# Create PR using gh CLI
gh pr create --title "feat: add user authentication" --body "..."
```

### PR Template

Use a `.github/pull_request_template.md`:

```markdown
## Summary

<Brief description of changes>

## Changes

- <List of specific changes>

## Testing

<How to test these changes>

## Checklist

- [ ] Tests pass
- [ ] Linting passes
- [ ] Documentation updated
```

### PR Title Format

Follow conventional commits:

```text
feat: add new feature
fix: resolve bug in authentication
docs: update README
refactor: simplify payment logic
```

## Code Review

### Requesting Review

```bash
# Request specific reviewers
gh pr create --reviewer user1,user2

# Add reviewers to existing PR
gh pr edit 123 --add-reviewer user1
```

### Review Checklist

- [ ] Code follows project style guidelines
- [ ] Tests cover new functionality
- [ ] No security vulnerabilities
- [ ] Documentation is updated
- [ ] No unnecessary complexity

### Addressing Feedback

```bash
# Make requested changes locally
git add .
git commit -m "fix: address review feedback"
git push

# Or squash into previous commit (if appropriate)
git commit --amend --no-edit
git push --force-with-lease
```

## Issues

### Creating Issues

```bash
gh issue create --title "Bug: login fails" --body "Description..."
```

### Issue Labels

Use consistent labels:

- `bug` - Something isn't working
- `enhancement` - New feature request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `priority: high/medium/low`

## GitHub CLI (gh)

### Essential Commands

```bash
# View PR details
gh pr view 123

# Check out PR locally
gh pr checkout 123

# Approve a PR
gh pr review 123 --approve --body "Looks good!"

# Request changes
gh pr review 123 --request-changes --body "Please fix..."

# Merge PR
gh pr merge 123 --merge

# Close PR without merging
gh pr close 123

# View workflow runs
gh run list

# Watch workflow run
gh run watch

# View issue
gh issue view 456

# List open PRs
gh pr list --state open

# List PRs by author
gh pr list --author username
```

## Workflows (GitHub Actions)

### Basic Workflow Structure

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm test
      - run: npm run lint
```

### Workflow Best Practices

- **Pin Actions**: Use SHA or specific version tags
- **Cache Dependencies**: Speed up builds
- **Fail Fast**: Stop on first error
- **Matrix Builds**: Test across multiple versions/OS

## Branch Protection

Recommended settings for `main`:

- Require pull request before merging
- Require approvals (at least 1)
- Dismiss stale reviews on new commits
- Require status checks to pass
- Require linear history (optional)

## Best Practices

- **Link Issues**: Reference issues in PRs with "Fixes #123" or "Closes #456"
- **Draft PRs**: Use draft status for work in progress
- **Auto-merge**: Enable auto-merge after required checks pass
- **CODEOWNERS**: Use `.github/CODEOWNERS` to auto-assign reviewers
- **Dependabot**: Enable for security updates

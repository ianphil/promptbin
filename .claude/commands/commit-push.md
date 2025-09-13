---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git push:*), Bash(make:*)
argument-hint: [commit-message]
description: Commit and push current work with code quality checks
---

# Commit and Push

## Context
- Current status: !`git status --porcelain`
- Current branch: !`git branch --show-current`

## Task
1. **Code Quality Checks**: Run code quality tools and fix any issues
   - `make format` - Format code with black
   - `make format-check` - Verify formatting is correct
   - `make lint` - Run flake8 linting
   - If any step fails, fix the issues and re-run until all checks pass
2. **Stage changes**: `git add .` (stage all changes including any formatting fixes)
3. **Commit**: If commit message provided in $ARGUMENTS, use it. Otherwise, create a short descriptive commit message based on the changes shown above.
4. **Commit**: `git commit -m "message"`
5. **Push**: `git push`

**Important**: Do not proceed with commit/push if any code quality checks fail. Fix all issues first.

Tell me what you committed and pushed, including any formatting/linting fixes that were applied.

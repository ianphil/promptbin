---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git push:*)
argument-hint: [commit-message]
description: Commit and push current work
---

# Commit and Push

## Context
- Current status: !`git status --porcelain`
- Current branch: !`git branch --show-current`

## Task
1. Stage all changes: `git add .`
2. If commit message provided in $ARGUMENTS, use it. Otherwise, create a short descriptive commit message based on the changes shown above.
3. Commit: `git commit -m "message"`
4. Push: `git push`

Tell me what you committed and pushed.

---
command: bump-minor
description: Bump the minor version by 1 and reset patch to 0
---

# Bump Minor Version

## Task
Increment the minor version (second number) by 1 and reset the patch version to 0 in all relevant files.

## Steps
1. Find current version in pyproject.toml
2. Parse the version (e.g., 0.3.2 -> major=0, minor=3, patch=2)
3. Increment minor by 1 and reset patch to 0 (e.g., 0.3.2 -> 0.4.0)
4. Update version in:
   - pyproject.toml
   - cli.py
5. Show the version change summary

## Important
- Bump the minor version (x.Y.z) and reset patch to 0
- Ensure all version references are updated consistently
- Do NOT commit the changes automatically
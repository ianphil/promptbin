---
command: bump-patch
description: Bump the patch version by 1
---

# Bump Patch Version

## Task
Increment the patch version (third number) by 1 in all relevant files.

## Steps
1. Find current version in pyproject.toml
2. Parse the version (e.g., 0.3.2 -> major=0, minor=3, patch=2)
3. Increment patch by 1 (e.g., 0.3.2 -> 0.3.3)
4. Update version in:
   - pyproject.toml
   - cli.py
5. Show the version change summary

## Important
- Only bump the patch version (x.y.Z)
- Ensure all version references are updated consistently
- Do NOT commit the changes automatically
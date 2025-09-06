---
allowed-tools: Read(*), Glob(*), Grep(*), ExitPlanMode(*)
argument-hint: <prompt-file>
description: Review a prompt file and create an implementation plan
---

# Review Prompt and Create Plan

## Context
- Target prompt file: $ARGUMENTS
- Working directory: !`pwd`
- Current git status: !`git status --porcelain`

## Task
1. Read and analyze the specified prompt file: `$ARGUMENTS`
2. Review the current codebase to understand what's already implemented
3. Identify gaps between current implementation and prompt requirements
4. Create a comprehensive implementation plan using the ExitPlanMode tool
5. The plan should include:
   - Current state analysis (what's done vs what's needed)
   - Step-by-step implementation approach
   - Technical considerations and dependencies
   - Estimated scope and complexity

## Usage
```
/review-prompt ai_docs/prompts/05_add_search_navigation.md
```

Review the prompt file thoroughly and provide a detailed implementation plan.